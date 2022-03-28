"""
    This module defines the blueprint for the devices API that can be integrated
    into a Flask app. It is intentionally declared separately so it is up to the
    operations team whether they want to host this API separately or in
    conjunction with another set of APIs.
"""
from datetime import date
from flask import (
    Blueprint,
    request,
    jsonify,
)

from .common import error_response
from .. import models
import logging
logger = logging.getLogger()

USERS_API_BLUEPRINT = Blueprint("users", __name__)

class UserEndpoint:

    @staticmethod
    def create():
        data = request.json
        errors = []
        if 'user_id' in data:
            errors.append("Do not provide a user id when creating a new user.")

        required_fields = [
            ("dob", lambda x: date.fromisoformat(x)),
            ("first_name", lambda x: str(x)),
            ("last_name", lambda x: str(x)),
            ("email", lambda x: str(x)),
            ("password", lambda x: str(x)),
        ]

        kwargs = {}
        for field, func in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
            else:
                try:
                    value = func(data[field])
                    kwargs[field] = value
                except Exception as err:
                    errors.append(f"{field} error: {str(err)}")
        if errors:
            logger.debug("Missing required field: ", errors)
            return error_response(errors, 422)

        existing = models.get_storage("users").users.query(email=data['email'])
        if existing:
            errors.append(f"User {data['email']} already exists.")
            logger.debug("Trying to create duplicate user: ", errors)
            return error_response(errors=errors, status_code=409)

        if "role_ids" not in data:
            errors.append("Missing required field: role_ids")
        else:
            role_ids = data['role_ids']
            kwargs['roles'] = roles = []
            for rid in role_ids:
                role = models.get_storage("users").user_roles.get(rid)
                if not role:
                    errors.append(f"Role does not exist with id: {rid}")
                    break
                else:
                    roles.append(role)

        if "patient_ids" in data:
            if data['patient_ids']:
                patients = models.get_storage("users").get(data['patient_ids'])
            else:
                patients = []

            if not all(patients):
                unknown = []
                for p, req in zip(patients, data['patient_ids']):
                    if p is None:
                        unknown.append(req)
                errors.append("Unknown user ids for patients: %s" % (", ".join(unknown)))
            else:
                kwargs['patients'] = patients

        if "medical_staff_ids" in data:
            if data['medical_staff_ids']:
                staff = models.get_storage("users").users.get(data["medical_staff_ids"])
            else:
                staff = []

            if not all(staff):
                unknown = []
                for p, req in zip(staff, data['patient_ids']):
                    if p is None:
                        unknown.append(req)
                errors.append("Unknown user ids for patients: %s" % (", ".join(unknown)))
            else:
                kwargs['medical_staff'] = staff

        if errors:
            return error_response(errors)
        else:
            user = models.User(**kwargs)
            user.password = models.hashUserPassword(user.email, user.password)
            user = models.get_storage("users").users.create(user)
            return jsonify(user=user.to_json())

    @staticmethod
    def query(role=None):
        roles = models.get_storage("users").user_roles.query(role_name=role)
        if not roles:
            users = []
        else:
            users = models.get_storage("users").users.query(roles=roles)

        return jsonify(users=[u.to_json() for u in users])

    @staticmethod
    def get(user_id=None, email=None):
        """Stuff"""
        if email is not None:
            users = models.get_storage("users").users.query(email=email)
            user = users[0] if len(users) else None
        else:
            user = models.get_storage("users").users.get(user_id=user_id)

        errors = []
        if not user:
            errors.append(f"User {user_id or email} does not exist.")
            return error_response(errors=errors, status_code=404)
        else:
            return jsonify(user=user.to_json())

    @staticmethod
    def update(user_id):
        user = models.get_storage("users").users.get(user_id)
        patch_data = request.json

        errors = []
        if not user:
            errors.append(f"User {user_id} does not exist.")
            return error_response(errors=errors, status_code=404)

        editable = ["first_name", "last_name"]
        for field in editable:
            current = getattr(user, field)
            value = patch_data.get(field, current)
            setattr(user, field, value)

        if "dob" in patch_data:
            try:
                user.dob = date.fromisoformat(patch_data['dob'])
            except ValueError:
                errors.append(f"Invalid date string: {patch_data['dob']}")

        role_ids = patch_data['role_ids']
        roles = []
        for rid in role_ids:
            role = models.get_storage("users").user_roles.get(rid)
            if not role:
                errors.append(f"Role does not exist with id: {rid}")
                break
            else:
                roles.append(role)

        user.roles = roles

        if "patient_ids" in patch_data:
            if patch_data['patient_ids']:
                patients = models.get_storage("users").users.get(patch_data['patient_ids'])
            else:
                patients = []

            if not all(patients):
                unknown = []
                for p, req in zip(patients, patch_data['patient_ids']):
                    if p is None:
                        unknown.append(req)
                errors.append("Unknown user ids for patients: %s" % (", ".join(unknown)))
            else:
                user.patients = patients

        if "medical_staff_ids" in patch_data:
            if patch_data['medical_staff_ids']:
                staff = models.get_storage("users").users.get(patch_data["medical_staff_ids"])
            else:
                staff = []

            if not all(staff):
                unknown = []
                for p, req in zip(staff, patch_data['patient_ids']):
                    if p is None:
                        unknown.append(req)
                errors.append("Unknown user ids for patients: %s" % (", ".join(unknown)))
            else:
                user.medical_staff = staff

        if errors:
            return error_response(errors=errors)

        user = models.get_storage("users").users.update(user)
        return jsonify(user=user.to_json())

    @staticmethod
    def delete(user_id):
        models.get_storage("users").users.delete(user_id)
        return "", 201

    @staticmethod
    def login(username, password):
        errors = []
        if not username or not password:
            errors.append("Username and password are both required.")
            return error_response(errors=errors, status_code=422)

        users = models.get_storage("users").users.query(email=username)
        user: models.User = users[0] if len(users) else None
        if not user:
            errors.append("User does not exit.")
            return error_response(errors=errors, status_code=404)
        else:
            hashed = models.hashUserPassword(user.email, password)
            if hashed != user.password:
                print(hashed, user.password)
                errors.append("Incorrect password.")
                return error_response(errors=errors, status_code=401)

        return jsonify(user=user.to_json()), 201

class UserRoleEndpoint:

    @staticmethod
    def list():
        roles = models.get_storage("users").user_roles.query()
        return jsonify(user_roles=[role.to_json() for role in roles])

    @staticmethod
    def create():
        name = request.json.get("role_name", "")
        errors = []
        if "role_name" not in request.json:
            errors.append("Missing required field: role_name")

        if errors:
            return error_response(errors=errors)

        role = models.UserRole(role_name=name)
        role = models.get_storage("users").user_roles.create(role)
        return jsonify(user_role=role.to_json())

    @staticmethod
    def get(role_id):
        role = models.get_storage("users").user_roles.get(role_id)
        if not role:
            return error_response(
                errors=[f"User role does not exist with id: {role_id}"],
                status_code=404)

        return jsonify(user_role=role.to_json())

    @staticmethod
    def update(role_id):
        role = models.get_storage("users").user_roles.get(role_id)
        errors = []
        if not role:
            errors.append(f"User role does not exist with id: {role_id}")
            return error_response(errors=errors, status_code=404)

        name = request.json.get("role_name", "").strip()
        if not name:
            errors.append("Missing required field: role_name")

        if errors:
            return error_response(errors=errors)

        role.role_name = name
        role = models.get_storage("users").user_roles.update(role)
        return jsonify(user_role=role.to_json())


@USERS_API_BLUEPRINT.route("", methods=["GET", "POST"])
def user_create():
    if request.method == "GET":
        email = request.args.get("email")
        role = request.args.get("role")

        if not email and not role:
            return error_response(["Only queries by email or role are supported."])

        if email is not None:
            return UserEndpoint.get(email=email)
        else:
            return UserEndpoint.query(role=role)
    else:
        return UserEndpoint.create()


@USERS_API_BLUEPRINT.route("/<int:user_id>", methods=["GET", "POST", "DELETE"])
def user(user_id: int):
    if request.method == "GET":
        return UserEndpoint.get(user_id)

    if request.method == "POST":
        return UserEndpoint.update(user_id)

    if request.method == "DELETE":
        return UserEndpoint.delete(user_id)

    return "", 501


@USERS_API_BLUEPRINT.route("/roles/<int:role_id>", methods=["GET", "POST"])
def user_role(role_id: int):
    if request.method == "GET":
        return UserRoleEndpoint.get(role_id)

    if request.method == "POST":
        return UserRoleEndpoint.update(role_id)

    return "", 501


@USERS_API_BLUEPRINT.route("/roles", methods=["GET", "POST"])
def user_role_create():
    if request.method == "GET":
        return UserRoleEndpoint.list()

    if request.method == "POST":
        return UserRoleEndpoint.create()

@USERS_API_BLUEPRINT.route("/login", methods=["POST"])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    return UserEndpoint.login(username, password)
