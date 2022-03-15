# Ramon Evans raevans@bu.edu Copyright 2022
#!/usr/bin/python3

import atexit
import os
import dotenv
from flask import Flask
from .apis import MESSAGES_API_BLUEPRINT
from .models import init_db, deinit

APP = Flask(__name__)
APP.register_blueprint(MESSAGES_API_BLUEPRINT, url_prefix="/chat")

class Config:
    def __init__(self):
        self.mongo_connection_string = None
        self.mongo_chat_db_name = None
        self.sqlite_db_filename = None

    def load_from_env(self):
        dotenv.load_dotenv()
        self.mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
        if not self.mongo_connection_string:
            raise ValueError("Missing environement variable: MONGO_CONNECTION_STRING")

        self.mongo_chat_db_name = os.getenv("MONGO_CHAT_DATABASE_NAME")
        if not self.mongo_chat_db_name:
            raise ValueError("Missing environement variable: MONGO_CHAT_DATABASE_NAME")

        self.sqlite_db_filename = os.getenv("SQLITEDB_FILENAME")
        if not self.sqlite_db_filename:
            raise ValueError("Missing environment variable SQLITEDB_FILENAME")

    def init_app(self, app, from_env=False):
        if from_env:
            self.load_from_env()

        init_db(app, {
            "MONGO_CONNECTION_STRING": self.mongo_connection_string,
            "MONGO_DATABASE": self.mongo_chat_db_name,
        })


@APP.route("/")

def default_app():
    config = Config()
    config.init_app(APP, from_env=True)
    atexit.register(deinit, APP)
    return APP

if __name__ == "__main__":
    APP = default_app()
    APP.run("debug")