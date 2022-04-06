"""
This module contains the models for how data is defined in memory
when loaded from the data store.
"""
from __future__ import annotations

from typing import Optional
import attr
from attr import asdict

from datetime import datetime

from peewee import (
    DateTimeField,
    IntegerField,
    FloatField,
    CharField,
    AutoField
)

from .base import (
    BaseModel,
    SqliteStorage,
    register
)

DEVICE_TABLES = []
DATA_TABLES = []
DATUM_TO_MODEL = {}

@attr.s(auto_attribs=True, kw_only=True)
class Device:
    """The `Device` model represents the metadata associated with a device
    that can be collect data from users. Note that the device does not indicate
    anything about what data is collected from the device. When recording data
    the device id should be tagged by the recorded data. See the Data
    Parameters
    ----------
        device_id : int
            An internal identifier for the device. This field will be auto-generated
            when a new device is created.
        name : str
            A user facing name for the device.
        current_firmware_version : str
            Latest information about what firmware version was loaded
            on the device.
        date_of_purchase : Optional[datetime]
            The date when the device was purchased, if available
        serial_number : Optional[str]
            The serial number of the device.
        mac_address : Optional[str]
            If the device is a networked device, this field should
            contain the MAC address.
    """
    device_id: int
    current_firmware_version: Optional[str]
    date_of_purchase: Optional[datetime]
    serial_number: Optional[str]
    mac_address: Optional[str]
    # These fields are validated by property
    name: str

    def __attrs_post_init__(self):
        if not isinstance(self.name, str):
            raise ValueError("name must be a string.")

        if not self.name.strip():
            raise ValueError("name cannot be blank.")

    def to_dict(self) -> dict:
        """Convert the model into a dict representation for serialization.
        Returns
        -------
        A dictionary with keys/value pairs of the device attributes
        """
        return asdict(self)


@attr.s(auto_attribs=True, kw_only=True)
class DeviceDatum:
    """Base class for different device datum types. This class should
    not be used directly.
    Parameters
    ----------
        device_id : int
            The identifier of the device that recired that recorded the data.
            This field is optional.
        assigned_user : int
            The user ID of the patient from which the datum was collected.
        received_time : datetime
            The datetime stamp when the datum was received by the system.
        collection_time : datetime
            The datetime stamp when the datum was collected on the device.
    """
    device_id: int
    assigned_user: int
    received_time: datetime
    collection_time: datetime
    datum_id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert the model into a dict representation for serialization.
        Returns
        -------
        A dictionary with keys/value pairs of the device attributes
        """
        return asdict(self)

    def to_json(self) -> dict:
        """Converts the model and values into a json serializeable dictionary
        Returns
        -------
        A dictionary where all key/value pairs are JSON serializable.
        """
        data = self.to_dict()
        data['received_time'] = self.received_time.isoformat()
        data['collection_time'] = self.collection_time.isoformat()
        return data

    @classmethod
    def from_json(cls, data: dict) -> DeviceDatum:
        """Instantiate a DeviceDatum object from a json dict.
        Parameters
        ----------
        data : dict
            A dictionary of key value pairs that are json serializeable
        Returns
        -------
        An instance of the device datum class.
        """

        received_time = datetime.fromisoformat(data.pop('received_time'))
        collection_time = datetime.fromisoformat(data.pop('collection_time'))
        return cls(**data,
                   received_time=received_time,
                   collection_time=collection_time)


@attr.s(auto_attribs=True, kw_only=True)
class TemperatureDatum(DeviceDatum):
    """A temperature datum
    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.
    Parameters
    ----------
    deg_c : float
        Temperature value in degrees C
    """
    deg_c: float


@attr.s(auto_attribs=True, kw_only=True)
class BloodPressureDatum(DeviceDatum):
    """A blood pressure datum
    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.
    Parameters
    ----------
    systolic : float
        The systolic measurement
    diastolic : float
        The diastolic measurement
    """
    systolic: float
    diastolic: float


@attr.s(auto_attribs=True, kw_only=True)
class GlucometerDatum(DeviceDatum):
    """A glucose level reading
    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.
    Parameters
    ----------
    mg_dl : int
        The blood sugar level in milligrams per deciliter
    """
    mg_dl: int


@attr.s(auto_attribs=True, kw_only=True)
class PulseDatum(DeviceDatum):
    """A heart rate dataum
    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.
    Parameters
    ----------
    bpm : int
        The measured heart rate in beats per minute.
    """
    bpm: int


@attr.s(auto_attribs=True, kw_only=True)
class WeightDatum(DeviceDatum):
    """A weight datum
    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.
    Parameters
    ----------
    grams : int
        Weight record in grams
    """
    grams: int


@attr.s(auto_attribs=True, kw_only=True)
class BloodSaturationDatum(DeviceDatum):
    """Blood saturation datum
    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.
    Parameters
    ----------
    percentage : float
        The blood saturation percentage.
    """
    percentage: float


@attr.s(auto_attribs=True, kw_only=True)
class DeviceAssignment:
    """The device assignment is a record of time periods when a device has been
    assigned to a user. Data collected during this time.
    Parameters
    ----------
    device_id : int
        The ID of the device assigned
    patient_id : int
        The user ID of the patient to whom the device is assigned.
    assigner_id : int
        The user ID of the medical professional who authorized the device
        to be assigned to the patient.
    date_assigned : datetime
        The start date and time when the user is assigned the device.
    date_returned : Optional[datetime]
        The date when the device is no longer recording data from the patient.
        This field should be set to None
    """

    device_id: int
    patient_id: int
    assigner_id: int
    date_assigned: datetime
    date_returned: Optional[datetime]


@register(DEVICE_TABLES)
class DeviceModel(BaseModel):
    """A storage model type to persist Devices.
    Storage models must have the same properties as the data classes they
    represent. See :class:`Device` for a description of the fields.
    """
    device_id = AutoField()
    name = CharField(unique=True)
    current_firmware_version = CharField(null=True)
    date_of_purchase = DateTimeField(null=True)
    serial_number = CharField(null=True)
    mac_address = CharField(null=True, max_length=100)

    def to_dataclass(self) -> Device:
        """Create a Device data class from a model instance."""
        return Device(
            device_id=self.device_id,
            current_firmware_version=self.current_firmware_version,
            date_of_purchase=self.date_of_purchase,
            serial_number=self.serial_number,
            mac_address=self.mac_address,
            name=self.name
        )

    @classmethod
    def from_dataclass(cls, device: Device) -> DeviceModel:
        """Create a DeviceModel instance from a data class instance."""
        return cls(
            current_firmware_version=device.current_firmware_version,
            date_of_purchase=device.date_of_purchase,
            serial_number=device.serial_number,
            mac_address=device.mac_address,
            name=device.name
        )


@register(DATA_TABLES)
class DeviceDatumModel(BaseModel):
    """A base model type that describes the fields common to all datum types.
    Storage models must have the same properties as the data classes they
    represent. See :class:`DeviceDatum` for a description of the fields.
    """
    datum_id = AutoField()
    device_id = IntegerField(null=False)
    assigned_user = IntegerField(null=False)
    received_time = DateTimeField(null=False)
    collection_time = DateTimeField(null=False)

    @classmethod
    def from_dataclass(cls, instance: DeviceDatum) -> DeviceDatumModel:
        """This classmethod is used to automate the conversion between
        dataclasses, which are the storage agnostic classes representing
        data, and the relational model.
        This methanism relies on keeping the collection of properties in sync.
        Yes, this is overhead and duplication, but it keeps the in-memory
        representation of the models completely separate from how they are
        stored in the rest of the application.
        Note that this is is defined here, but this class shouldn't be used
        directly. It should always be called from a subclass.
        Parameters
        ----------
        instance : DeviceDatum
            The datum instance to convert into the model class.
        Returns
        -------
        An instance of the device datum model.
        """
        attrs = {}
        for field in cls._meta.sorted_fields:
            if not hasattr(instance, field.name):
                raise AttributeError(f"Dataclass for {cls.__name__} does not have "
                                     f"the attribute {field.name}. You must override"
                                     f"the from_dataclass method in this submodel.")
            else:
                attrs[field.name] = getattr(instance, field.name)

        return cls(**attrs)

    def to_dataclass(self) -> DeviceDatum:
        """Convert this model into the appropriate dataclass
        Returns
        -------
        An instance of the dataclass for the appropriate datum type.
        """

        DatumClass = None
        for data_cls, model_cls in DATUM_TO_MODEL.items():
            if isinstance(self, model_cls):
                DatumClass = data_cls

        attrs = {}
        for field in self._meta.sorted_fields:
            attrs[field.name] = getattr(self, field.name)

        return DatumClass(**attrs)


@register(DATA_TABLES)
class TemperatureDatumModel(DeviceDatumModel):
    """Temperature Datum"""
    deg_c = FloatField(null=False)


@register(DATA_TABLES)
class BloodPressureDatumModel(DeviceDatumModel):
    """Blood Pressure Datum"""
    systolic = FloatField()
    diastolic = FloatField()


@register(DATA_TABLES)
class GlucometerDatumModel(DeviceDatumModel):
    """Glucometer Datum"""
    mg_dl = IntegerField()


@register(DATA_TABLES)
class PulseDatumModel(DeviceDatumModel):
    """Pulse Datum"""
    bpm = IntegerField()


@register(DATA_TABLES)
class WeightDatumModel(DeviceDatumModel):
    """Weight Datum"""
    grams = IntegerField()


@register(DATA_TABLES)
class BloodSaturationDatumModel(DeviceDatumModel):
    """Blood Saturation Datum"""
    percentage = FloatField()


class DeviceStorage(SqliteStorage):
    """SqliteStorage Implementation for devices"""

    tables = DEVICE_TABLES

    def query(self):
        query = DeviceModel.select()
        models = list(query)
        return [m.to_dataclass() for m in models]

    def get(self, device_id: int) -> Optional[Device]:
        """Get a device by its id.
        Parameters
        ----------
        device_id : int
            The device identifier assigned when the device was created.
        Returns
        -------
        None if the device does not exist, otherwise a Device instance.
        """
        query = DeviceModel.select().where(DeviceModel.device_id == device_id)
        if query.count() == 0:
            return None

        model: DeviceModel = query[0]
        return model.to_dataclass()

    def create(self, device: Device) -> Device:
        """Create a new device.
        Parameters
        ----------
        device : Device
            An instance of the device dataclass with attributes filled in for the
            new device. This method will raise a ValueError if the device.device_id
            proerty is not None. A device id will be generated as part of this process
            and set on the returned instance.
        Returns
        -------
        A Device instance.
        """
        if device.device_id is not None:
            raise ValueError("device_id must be None when creating a new device.")

        model = DeviceModel.from_dataclass(device)
        model.save()
        return model.to_dataclass()

    def update(self, device: Device) -> Device:
        """Update an existing device.
        Parameters
        ----------
        device : Device
            An instance of the device to update. The value of the `device_id` property
            will be used to identify the record to update.
        Returns
        -------
        An updated Device instance.
        """
        query = DeviceModel.select().where(DeviceModel.device_id == device.device_id)
        if not query.count():
            raise ValueError(f"Device {device.device_id} does not exist.")

        model = query[0]
        model.name = device.name
        model.current_firmware_version = device.current_firmware_version
        model.date_of_purchase = device.date_of_purchase
        model.serial_number = device.serial_number
        model.mac_address = device.mac_address
        model.save()
        return model.to_dataclass()

    def delete(self, device_id: int) -> bool:
        """Delete a device.
        Parameters
        ----------
        device_id : int
            The id of the device to delete
        Returns
        -------
        True if the device was deleted, False otherwise.
        """
        query = DeviceModel.delete().where(DeviceModel.device_id == device_id)
        n_rows_deleted = query.execute()
        return n_rows_deleted >= 1

# TODO: Turn this into a class decorator.
DATUM_TO_MODEL = {
    # NOTE: DeviceDatum is intentionally commented out. All data are subclasses
    # of this type and it should not be used to identify a dataclass. This
    # DeviceDatum: DeviceDatumModel,
    TemperatureDatum: TemperatureDatumModel,
    BloodPressureDatum: BloodPressureDatumModel,
    GlucometerDatum: GlucometerDatumModel,
    PulseDatum: PulseDatumModel,
    WeightDatum: WeightDatumModel,
    BloodSaturationDatum: BloodSaturationDatumModel
}

class DataStorage(SqliteStorage):
    """A SQLite storage class for device data."""

    tables = DATA_TABLES

    def _model_for_instance(self, instance: DeviceDatum) -> DeviceDatumModel:
        """Get the peewee.Model class definition that corresponds
        to the Datum instance type passed in.
        Parameters
        ----------
        instance : DeviceDatum
            An instance of a datum subclass.
        Returns
        -------
        The corresponding SQLite model class definition for the DeviceDatum instance passed in.
        Raises
        ------
        ValueError if there is no dataclass mapping for the DeviceDatum instance
        passd in.
        """
        for datum_cls, model_cls in DATUM_TO_MODEL.items():
            if isinstance(instance, datum_cls):
                return model_cls

        raise ValueError(f"No datum class found for instance: {instance.__name__}")

    def create(self, data: DeviceDatum):
        """Log a device datum to the database."""
        Model = self._model_for_instance(data)
        instance = Model.from_dataclass(data)
        instance.save()
        return instance.to_dataclass()

    def delete(self, datum_id: int):
        raise NotImplementedError("Data cannot be deleted once logged into the database.")

    def update(self, datum_id: int):
        """Data cannot be updated once logged to the database."""
        raise NotImplementedError("Data cannot be updated once logged into the database.")

    def query(self):
        """"Query data from the database. Currently this only
        allows a very inefficient select all query on all datum
        models. This should be extended quite a bit to support
        filtering data."""
        data = []
        for model in DATUM_TO_MODEL.values():
            data.extend(list(model.select()))

        data = sorted(data, key=lambda d: d.collection_time)
        return [m.to_dataclass() for m in data]


def store_data(data: list[DeviceDatum], storage: DataStorage):
    """A helper function to persist data to the database.
    Parameters
    ----------
    data : list[DeviceDatum]
        Sepcific data instances to be logged to the database.
    storage : DataStorage
        The instance of the data storage proxy used to persists
        data.
    """
    return list(map(storage.create, data))
