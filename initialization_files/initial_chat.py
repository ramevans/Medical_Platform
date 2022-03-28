# Ramon Evans raevans@bu.edu Copyright 2022
#!/usr/bin/python3

from pathlib import pathlib
from .chat_model import MessageStore

from flask import current_app
from typing import Optional

def init_database(app, config):
	devices_file = config.get("DEVICES_FILENAME", "")
    data_db_file = config.get("DATA_DB_FILENAME", "")
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

    if mongo_connection and mongo_database:
        app.config["STORAGE"]["messages"] = MessageStore(mongo_connection, mongo_database)

def deinit(app):
    dev_storage: Optional[DeviceStorage] = app.config['STORAGE'].get("devices")
    if dev_storage:
        dev_storage.deinit()

    data_storage: Optional[DataStorage] = app.config['STORAGE'].get("data")
    if data_storage:
        data_storage.deinit()


def get_storage(name) -> Storage:
    """Return the configured storage
    """
    if name not in current_app.config['STORAGE']:
        raise ValueError(f"Storage for {name} does not exist")

    return current_app.config['STORAGE'][name]

