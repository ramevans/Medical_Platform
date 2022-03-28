"""
    This module defines the blueprint for the devices API that can be integrated
    into a Flask app. It is intentionally declared separately so it is up to the
    operations team whether they want to host this API separately or in
    conjunction with another set of APIs.
"""
import peewee
from flask import (
    Blueprint,
    request,
    make_response,
    jsonify
)

from .common import error_response
from .. import models

# TODO: Make this configurable
DEVICES_API_BLUEPRINT = Blueprint("devices", __name__)


@DEVICES_API_BLUEPRINT.route("", methods=["GET"])
def device_query():
    devices = models.get_storage("devices")
    existing = devices.query()
    return jsonify(devices=[e.to_dict() for e in existing])

@DEVICES_API_BLUEPRINT.route("", methods=["POST"])
def device_create():
    """Create a new device.
    When registered with a Flask app, this method will handle when the
    user sends a HTTP PUT request to <base_uri>/devices/<device_id>
    See the HTTP API documentation for information about the payload
    structure.
    """
    data = request.get_json()
    if data is None:
        # The request data format was not valid.
        return make_response("Invalid JSON request."), 400

    # Create an empty errors array
    errors = []
    required_fields = ["name"]
    for field in required_fields:
        if field not in data.keys():
            errors.append(f"Missing required field: {field}")

    if not errors:
        try:
            device = models.get_storage("devices").create(models.Device(
                device_id=None,
                name=data["name"],
                current_firmware_version=data.get("current_firmware_version", None),
                mac_address=data.get("mac_address", None),
                serial_number=data.get("serial_number", None),
                date_of_purchase=data.get("date_of_purchase", None),
            ))
        except ValueError as err:
            errors.append(str(err))
        except peewee.IntegrityError as err:
            errors.append(str(err))

    if errors:
        return error_response(errors)

    return jsonify(device.to_dict())

class DeviceEndpoint:

    @staticmethod
    def put(device_id):
        """Update an existing device.
        When registered with a Flask app, this method will handle when the
        user sends a HTTP PUT request to <base_uri>/devices/<device_id>
        See the HTTP API documentation for information about the payload
        structure.
        Parameters
        ----------
            device_id: int
                The ID of the device to update
        """
        data = request.get_json()
        if data is None:
            # The request data format was not valid.
            return make_response("Invalid JSON request."), 400

        device = models.get_storage('devices').get(device_id)
        if not device:
            return "", 404

        editable_fields = [
            "name",
            "current_firmware_version",
            "date_of_purchase",
            "serial_number",
            "mac_address",
        ]

        # Create an empty errors array
        errors = []
        for field in data:
            if field in editable_fields:
                try:
                    setattr(device, field, data[field])
                except ValueError as err:
                    errors.append(str(err))
            else:
                if data[field] != getattr(device, field):
                    errors.append(f"'{field}' is not editable.")

        if errors:
            return error_response(errors)
        else:
            # We don't want to save the model if there were errors
            updated = models.get_storage("devices").update(device)
            return jsonify(updated.to_dict()), 200

    @staticmethod
    def get(device_id: int):
        """
        """
        device = models.get_storage("devices").get(device_id)
        if not device:
            return make_response("Not found"), 404

        return jsonify(device.to_dict()), 200

    @staticmethod
    def delete(device_id):
        deleted = models.get_storage("devices").delete(device_id)
        if deleted:
            return "", 200
        else:
            return "", 404


@DEVICES_API_BLUEPRINT.route("/<int:device_id>", methods=["GET", "PUT", "DELETE"])
def single_device_route(device_id):
    if request.method == "GET":
        return DeviceEndpoint.get(device_id)
    elif request.method == "DELETE":
        return DeviceEndpoint.delete(device_id)
    elif request.method == "PUT":
        return DeviceEndpoint.put(device_id)
    else:
        # The flask decorator will prevent this from getting here if the method
        # isn't supported. If we get here it means the method is supported by
        # not yet implemented.
        return "Not implemented", 501
