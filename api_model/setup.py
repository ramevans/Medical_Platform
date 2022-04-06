"""
This module provides some base definitions and functions used by
other model modules.
"""

from peewee import (
    Model,
    SqliteDatabase,
)


class BaseModel(Model):
    """Recommended practice is to have a base model that
    your tables inherit from."""
    pass

class Storage:
    """An abstract interface class for storage proxies. The
    main intent of this class is to define the API that all
    storage implementations should implement."""

    def query(self):
        raise NotImplementedError()

    def get(self, record_id: int):
        raise NotImplementedError()

    def create(self, model):
        raise NotImplementedError()

    def update(self, model):
        raise NotImplementedError()

    def delete(self, record_id: int) -> bool:
        raise NotImplementedError()


class SqliteStorage(Storage):
    """An abstract base storage base flass class for a storage proxy
    that reads and writes to a SQLite database.
    Attributes
    ----------
    tables : list[BaseModel]
        A list of tables that this storage proxy needs to read and write
        from. The tables will get created at runtime when an instance
        of this class is created.
    Parameters
    ----------
    filename : str
        The filename of the sqlite database to use. This will be created if
        it doesn't not exist. After initializing, the storage class will maintain
        an open handle to the database.
    """

    tables: list[BaseModel] = None

    def __init__(self, filename):
        if not self.tables:
            raise ValueError("SqliteStorage subclass define tables class property.")

        self.database = SqliteDatabase(filename, pragmas={'foreign_keys': 1})
        self.database.bind(self.tables)
        self.database.connect()

        to_create = [model for model in self.tables if not model.table_exists()]
        self.database.create_tables(to_create)

    def __setattr__(self, attr, value):
        if attr == "tables":
            raise Exception("tables should not be overwritten at runtime.")

        return super().__setattr__(attr, value)

    def deinit(self):
        """Cleans up the database connection"""
        if self.database:
            self.database.close()


def register(array):
    """A decorator register a class or function by appending
    it to an array.
    """
    def wrapper(cls):
        array.append(cls)
        return cls

    return wrapper
