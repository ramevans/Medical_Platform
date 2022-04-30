"""
This module provides the APIs for storing and retrieving
data from the system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from flask import (
    Blueprint,
    request,
    jsonify
)

from .common import error_response
from ..models import device_models, get_storage

DATA_API_BLUEPRINT = Blueprint("data", __name__)

MODEL_TYPE_NAMES = {
    "temperature": device_models.TemperatureDatum,
    "blood_pressure": device_models.BloodPressureDatum,
    "oxygen_saturation": device_models.BloodSaturationDatum,
    "glucose_level": device_models.GlucometerDatum,
    "heart_rate": device_models.PulseDatum,
    "weight": device_models.WeightDatum
}

@dataclass
class JSONDatum:
    device_id: int
    collection_time: datetime
    data_type: str
    data: dict
    assigned_user: Optional[int] = None


class Endpoints:

    @staticmethod
    def get():
        data = get_storage("data").query()
        return jsonify(data=[d.to_dict() for d in data])

    @staticmethod
    def post():
        if not request.headers['Content-Type'] == "application/json":
            return "Unsupported content type.", 422

        body = request.json
        if "data" not in body:
            return error_response(["Missing required object key: \"data\""])

        datapoints = body["data"]
        if not isinstance(datapoints, list):
            return error_response(["\"data\" must be a list of data points."])

        errors = []
        to_store = []
        for i, payload in enumerate(datapoints):
            try:
                posted = JSONDatum(**payload)
                data_type = posted.data_type
                if data_type not in MODEL_TYPE_NAMES:
                    errors.append(f"Invalid data type: {data_type}")
                    continue

                received_time = datetime.now()
                assigned_user = posted.assigned_user
                if assigned_user is None:
                 
                    assigned_user = -1

                data = posted.data
                datum = MODEL_TYPE_NAMES[data_type](
                    device_id=posted.device_id,
                    assigned_user=assigned_user,
                    received_time=received_time,
                    collection_time=datetime.fromisoformat(posted.collection_time),
                    **data
                )

                to_store.append(datum)
            except (TypeError, ValueError) as err:
                errors.append(f"Error processing data point {i}: {err}")

        if errors:
            return error_response(errors=errors)

        device_models.store_data(to_store, get_storage("data"))
        return "", 201


@DATA_API_BLUEPRINT.route("", methods=["GET", "POST"])
def data_endpoints():
    if request.method == "GET":
        return Endpoints.get()
    elif request.method == "POST":
        return Endpoints.post()
    else:
        return "Not Implemented", 501
