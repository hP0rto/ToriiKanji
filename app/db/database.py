"""
Database connection and initialization for ToriiKanji.
Uses programmatic schema creation instead of template copying.
"""

import gzip
import json
import os
import sqlite3

from db.schema import ALL_TABLES, CREATE_INDEXES, SCHEMA_VERSION
from utils.paths import DB_PATH, KANJI_SEED_PATH


def dict_factory(cursor, row):
    """Convert sqlite3 rows to dictionaries."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class _ClosingConnection(sqlite3.Connection):
    """
    Connection whose context manager also closes it (the stock sqlite3 one only
    commits/rolls back, leaking a connection per `with` block) and logs failures
    before re-raising them, so callers/workers can surface them to the UI.
    """

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is not None:
                print(f"Database error: {exc_type.__name__}: {exc_value}")
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()



def seed_kanji_dict(cursor):
    """
    Populate kanji_dict from the bundled seed file if the table is empty.
    Returns the number of rows inserted.
    """
    if cursor.execute("SELECT 1 FROM kanji_dict LIMIT 1").fetchone():
        return 0

    if not KANJI_SEED_PATH.is_file():
        print(f"Warning: kanji seed file not found at {KANJI_SEED_PATH}")
        return 0

    with gzip.open(KANJI_SEED_PATH, "rt", encoding="utf-8") as f:
        data = json.load(f)

    columns = data["columns"]
    placeholders = ", ".join("?" for _ in columns)
    cursor.executemany(
        f"INSERT OR IGNORE INTO kanji_dict ({', '.join(columns)}) VALUES ({placeholders})",
        data["rows"],
    )
    return cursor.rowcount


def init_database():
    """
    Initialize the database by creating all tables and indexes.
    Safe to call multiple times (uses IF NOT EXISTS).
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()

        # Create all tables
        for create_sql in ALL_TABLES:
            cursor.execute(create_sql)

        # Create indexes
        for index_sql in CREATE_INDEXES:
            cursor.execute(index_sql)

        # Fill the kanji dictionary on first run
        seeded = seed_kanji_dict(cursor)
        if seeded:
            print(f"Seeded kanji_dict with {seeded} entries")

        # Record schema version
        cursor.execute(
            "INSERT OR IGNORE INTO schema_version (version) VALUES (?)",
            (SCHEMA_VERSION,)
        )

        conn.commit()
        print(f"Database initialized at: {DB_PATH} (schema v{SCHEMA_VERSION})")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()


def get_connection():
    """
    Get a database connection with dict row factory.
    Initializes the database on first call if it doesn't exist.
    """
    if not os.path.exists(DB_PATH):
        init_database()

    conn = sqlite3.connect(DB_PATH, factory=_ClosingConnection)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
