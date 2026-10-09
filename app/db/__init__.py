"""Database package: connection helpers and schema initialization."""

from db.database import get_connection, init_database

__all__ = ["get_connection", "init_database"]
