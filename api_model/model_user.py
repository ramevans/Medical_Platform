"""
    This module contains the models representing users and user roles
    in the MedOps system.
"""
from datetime import date
import attr
from attr import asdict, field
from typing import Optional, Union
from peewee import (
    AutoField,
    TextField,
    ForeignKeyField,
    DateField
)

from .base import (
    BaseModel,
    SqliteStorage,
    register
)

USER_TABLES = []
USER_ROLE_TABLES = []

@attr.s(auto_attribs=True, kw_only=True)
class UserRole:
    """Simple class to define user roles that can be assigned to users.
    Parameters
    ----------
    role_id : Optional[int]
        The identifier for the role. This should be assigned automatically
        by the underlying storage mechanism.
    role_name : str
        A human friendly name for the role.
    """
    role_id: Optional[int] = None
    role_name: str

    def to_dict(self) -> dict:
        """Serialize the UserRole class as a dictionary"""
        return asdict(self)

    def to_json(self):
        """Serialize the UserRole class as a dictionary that is
        json serializable"""
        return self.to_dict()

def hashUserPassword(email: str, password: str):
    if isinstance(email, str):
        email = email.encode()

    if isinstance(password, str):
        password = password.encode()

    import hashlib
    hasher = hashlib.sha256()
    hasher.update(email)
    hasher.update(password)
    return hasher.hexdigest()


@attr.s(auto_attribs=True, kw_only=True)
class User:
    """Data class representing a user.
    Parameters
    ----------
    user_id : Optional[int]
        The internal identifier for the user. This should be None when
        creating a new user and will be automatically assigned the storage
        mechanism.
    dob : date
        The birthdate of the user
    first_name : str
        The user's first name
    last_name : str
        The user's last name
    roles : list[UserRole]
        A list of roles to which the user is assigned. These must correspond
        to existing UserRoles in the database.
    relationships: list[int]
        A list of other users to which the this user is related. This field
        should be used to associate doctors and nurses with patients.
    """
    user_id: Optional[int] = None
    dob: date
    first_name: str
    last_name: str
    email: str
    password: str
    roles: list[UserRole]
    patients: list[int] = field(factory=list)
    medical_staff: list[int] = field(factory=list)

    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def to_dict(self) -> dict:
        data = asdict(self)
        return data

    def to_json(self):
        data = self.to_dict()
        data.pop("password")
        data['dob'] = data['dob'].isoformat()

        for m in data['medical_staff']:
            m['dob'] = m['dob'].isoformat()
            m.pop('medical_staff')
            m.pop('patients')
            m.pop("password")
            m.pop("roles")

        for m in data['patients']:
            m['dob'] = m['dob'].isoformat()
            m.pop('patients')
            m.pop('medical_staff')
            m.pop("password")
            m.pop("roles")
        return data


@register(USER_TABLES)
class UserModel(BaseModel):
    """The relational model for persisting Users
    See the User class for a description of the parameters.
    Note that roles is not a database field. This allows the model to do
    what is necessary in terms of converting between UserRole instances
    and whatever mechanism is implemented for storing the many-to-many
    relationship.
    """
    user_id = AutoField()
    dob = DateField()
    first_name = TextField()
    last_name = TextField()
    email = TextField()
    password = TextField()
    roles = None

    def to_dataclass(self) -> User:
        """Create a Device data class from a model instance."""
        self.roles = []
        for relation in self.userroles.select():
            self.roles.append(relation.role.to_dataclass())

        patients = []
        for p in self.patients:
            patients.append(User(
                user_id=p.patient.user_id,
                dob=p.patient.dob,
                first_name=p.patient.first_name,
                last_name=p.patient.last_name,
                roles=p.patient.roles,
                email=p.patient.email,
                password=p.patient.password,
                patients=[],
                medical_staff=[]
            ))

        medical_staff = []
        for p in self.medical_staff:
            medical_staff.append(User(
                user_id=p.professional.user_id,
                dob=p.professional.dob,
                first_name=p.professional.first_name,
                last_name=p.professional.last_name,
                roles=p.professional.roles,
                email=p.professional.email,
                password=p.professional.password,
                patients=[],
                medical_staff=[]
            ))

        return User(
            user_id=self.user_id,
            dob=self.dob,
            first_name=self.first_name,
            last_name=self.last_name,
            roles=self.roles,
            patients=patients,
            medical_staff=medical_staff,
            email=self.email,
            password=self.password
        )

    def _update_user_roles(self):
        query = UserRoleUserModel.select().where(
            UserRoleUserModel.user_id == self.user_id)

        existing_roles = {x.role_id for x in query}
        requested_roles = {x.role_id for x in self.roles}

        to_delete = existing_roles - requested_roles
        to_create = requested_roles - existing_roles

        for role_id in to_create:
            UserRoleUserModel.create(role_id=role_id, user_id=self.user_id)

        for role_id in to_delete:
            query = UserRoleUserModel.delete().where(
                (UserRoleUserModel.role_id == role_id) & (UserRoleUserModel.user_id == self.user_id))
            query.execute()

    def save(self, *args, **kwargs):
        """Save a model to the database."""
        super().save(*args, **kwargs)
        to_keep = {u.professional.user_id for u in self.medical_staff}
        URM = UserRelationshipsModel
        URM.delete().where((URM.patient == self.user_id) & (URM.professional.not_in(to_keep))).execute()
        for r in self.medical_staff:
            r.save()

        to_keep = {u.patient.user_id for u in self.patients}
        for r in self.patients:
            r.save()
        URM.delete().where((URM.professional == self.user_id) & (URM.patient.not_in(to_keep))).execute()
        self._update_user_roles()

    @classmethod
    def from_dataclass(cls, user: User):
        """Create a DeviceModel instance from a data class instance."""
        instance = cls(
            user_id=user.user_id,
            dob=user.dob,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=user.roles,
            password=user.password,
            email=user.email,
            patients=[],
            medical_staff=[]
        )

        URM = UserRelationshipsModel
        for patient in user.patients:
            exists = URM.select().where((URM.patient == patient.user_id) & (URM.professional == user.user_id))
            if user.user_id and exists.count():
                instance.patients.append(exists[0])
            else:
                instance.patients.append(URM(patient=patient.user_id, professional=instance))

        for medical_staff in user.medical_staff:
            exists = URM.select().where((URM.professional == medical_staff.user_id) & (URM.patient == user.user_id))
            if user.user_id and exists.count():
                instance.medical_staff.append(exists[0])
            else:
                instance.medical_staff.append(URM(professional_id=medical_staff.user_id, patient=instance))

        return instance


@register(USER_ROLE_TABLES)
class UserRoleModel(BaseModel):
    """Relational model for persisting user roles.
    See the UserRole class for a description of the different fields.
    """
    role_id = AutoField()
    role_name = TextField()

    def to_dataclass(self) -> UserRole:
        """Create a Device data class from a model instance."""
        return UserRole(
            role_id=self.role_id,
            role_name=self.role_name
        )

    @classmethod
    def from_dataclass(cls, user_role: UserRole):
        """Create a DeviceModel instance from a data class instance."""
        return cls(
            role_id=user_role.role_id,
            role_name=user_role.role_name
        )

@register(USER_TABLES)
class UserRoleUserModel(BaseModel):
    """A many to many replationship for associating users with roles."""
    user = ForeignKeyField(UserModel, backref="userroles")
    role = ForeignKeyField(UserRoleModel, backref="userroles")


@register(USER_TABLES)
class UserRelationshipsModel(BaseModel):
    id = AutoField()
    # IMPORTANT! The backrefs are swapped. If I'm a doctor with user_id 1,
    # and UserRelationship record where professional.user_id == 1 contains my
    # patients.
    professional = ForeignKeyField(UserModel, backref="patients")
    patient = ForeignKeyField(UserModel, backref="medical_staff")


class UserModelStorage(SqliteStorage):
    """Storage class for persisting UserModels to a sqlite database"""
    tables = USER_TABLES

    def query(self, email=None, roles=None):
        query = UserModel.select()
        if email is not None:
            query = query.where(UserModel.email == email)

        users = [u.to_dataclass() for u in query]

        if roles is not None:
            ids = set([r.role_id for r in roles])
            to_return = []
            for user in users:
                if set([r.role_id for r in user.roles]) & ids:
                    to_return.append(user)

            users = to_return

        return users

    def get(self, user_id: Union[list, int]) -> Optional[User]:
        if isinstance(user_id, int):
            user_ids = [user_id]
        else:
            user_ids = user_id

        query = UserModel.select().where(UserModel.user_id.in_(user_ids))
        if query.count() == 0:
            result = [None] * len(user_ids)
        else:
            result = [u for u in query]

        order = [None] * len(user_ids)
        for idx, uid in enumerate(user_ids):
            for user in result:
                if user is not None and user.user_id == uid:
                    order[idx] = user.to_dataclass()

        return order[0] if isinstance(user_id, int) else order

    def create(self, user: User) -> User:
        if user.user_id is not None:
            raise ValueError("Creating a user must not be none.")

        model = UserModel.from_dataclass(user)
        model.save()
        [r.save() for r in model.patients]
        [r.save() for r in model.medical_staff]
        return model.to_dataclass()

    def update(self, user: User) -> User:
        if user.user_id is None:
            raise ValueError("Use create_user method to create a new user.")

        model = UserModel.from_dataclass(user)
        model.save()
        return model.to_dataclass()

    def delete(self, user_id: int) -> bool:
        UserRoleUserModel.delete().where(UserRoleUserModel.user_id == user_id).execute()
        query = UserRelationshipsModel.delete().where(
            (UserRelationshipsModel.professional == user_id) | (UserRelationshipsModel.patient == user_id))
        query.execute()
        query = UserModel.delete().where(UserModel.user_id == user_id)
        n_rows_deleted = query.execute()
        return n_rows_deleted >= 1


class UserRoleModelStorage(SqliteStorage):
    """Storage class for persisting UserRoleModels to a sqlite database"""
    tables = USER_ROLE_TABLES

    def query(self, role_name=None):
        query = UserRoleModel.select()
        if role_name is not None:
            query = query.where(UserRoleModel.role_name == role_name)

        return [r.to_dataclass() for r in query]

    def get(self, role_id: int) -> Optional[UserRole]:
        query = UserRoleModel.select().where(UserRoleModel.role_id == role_id)
        if query.count() == 0:
            return None

        return query[0].to_dataclass()

    def create(self, role: UserRole) -> UserRole:
        model = UserRoleModel.from_dataclass(role)
        model.save()
        return model.to_dataclass()

    def update(self, role: UserRole) -> UserRole:
        query = UserRoleModel.select().where(UserRoleModel.role_id == role.role_id)
        if query.count() == 0:
            raise ValueError(f"User Role does not exist: {role.role_id}")

        model = query[0]
        model.role_name = role.role_name
        model.save()
        return model.to_dataclass()

    def delete(self, role_id: int) -> bool:
        query = UserRoleModel.delete().where(UserRoleModel.role_id == role_id)
        n_rows_deleted = query.execute()
        return n_rows_deleted >= 1


class UserRelationshipStorage(SqliteStorage):
    def query(self):
        pass

    def get(self, patient_id=None, professional_id=None):
        pass

    def create(self, patient_id=None, profession_id=None):
        pass


class UserStorage:
    """A wrapper class to expose user storage functionality. This model
    requires that both Users and UserRoles are stored in the same database
    Parameters
    ----------
    filename : str
        The file path to the sqlite database to use.
    Attributes
    ----------
    users : UserModelStorage
        A SqliteStorage implementation of user storage
    user_roles : UserRoleModelStorage
        A SqliteStorage implementation of user role storage
    """

    def __init__(self, filename):
        self.users = UserModelStorage(filename)
        self.user_roles = UserRoleModelStorage(filename)

    def deinit(self):
        self.users.deinit()
        self.user_roles.deinit()
