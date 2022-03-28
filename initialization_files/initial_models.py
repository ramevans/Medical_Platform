"""
    Models contain the in-memory storage data
"""
from pathlib import Path
from .device_models import DeviceStorage, DataStorage
from .user_models import UserStorage
from .base import Storage
from .device_models import Device # noqa: F401
from .user_models import User, UserRole # noqa: F401
from .user_models import hashUserPassword # noqa: F401
from .chat_model import MessageStore

from flask import current_app
from typing import Optional

def init_db(app, config):
    """Initialize the current application instance with the loaded
    config.
    Parameters
    ----------
    app : flask.Flask
        The flask app to configure.
    config : dict
        The application configuration.
    """
    devices_file = config.get("DEVICES_FILENAME", "")
    data_db_file = config.get("DATA_DB_FILENAME", "")
    users_db_file = config.get("USERS_DB_FILENAME", "")
    mongo_connection = config.get("MONGO_CONNECTION_STRING", "")
    mongo_database = config.get("MONGO_DATABASE", "")

    app.config["STORAGE"] = {}
    if devices_file:
        if isinstance(devices_file, str):
            devices_file = Path(devices_file)

        app.config["STORAGE"]["devices"] = DeviceStorage(devices_file)

    if data_db_file:
        if isinstance(data_db_file, str):
            data_db_file = Path(data_db_file)

        app.config["STORAGE"]["data"] = DataStorage(data_db_file)

    if users_db_file:
        if isinstance(users_db_file, str):
            users_db_file = Path(users_db_file)

        app.config["STORAGE"]["users"] = UserStorage(users_db_file)

    if mongo_connection and mongo_database:
        app.config["STORAGE"]["messages"] = MessageStore(mongo_connection, mongo_database)


def deinit(app):
    dev_storage: Optional[DeviceStorage] = app.config['STORAGE'].get("devices")
    if dev_storage:
        dev_storage.deinit()

    data_storage: Optional[DataStorage] = app.config['STORAGE'].get("data")
    if data_storage:
        data_storage.deinit()

    user_storage: Optional[UserStorage] = app.config['STORAGE'].get("users")
    if user_storage:
        user_storage.deinit()


def get_storage(name) -> Storage:
    """Return the configured storage
    """
    if name not in current_app.config['STORAGE']:
        raise ValueError(f"Storage for {name} does not exist")

    return current_app.config['STORAGE'][name]
