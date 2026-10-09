"""
Database schema definitions for ToriiKanji.
Creates all tables programmatically via SQL CREATE statements.
Replaces the old template-copy approach.
"""

# Schema version for future migration support
SCHEMA_VERSION = 1

# ─── Table Definitions ───────────────────────────────────────────────────────

CREATE_MEDIA_TABLE = """
CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE
);
"""

CREATE_CAPTURE_TABLE = """
CREATE TABLE IF NOT EXISTS capture (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_text TEXT,
    image_path TEXT,
    media_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (media_id) REFERENCES media(id) ON DELETE SET NULL
);
"""

CREATE_CAPTURE_KANJI_TABLE = """
CREATE TABLE IF NOT EXISTS capture_kanji (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capture_id INTEGER NOT NULL,
    kanji TEXT NOT NULL,
    UNIQUE(capture_id, kanji),
    FOREIGN KEY (capture_id) REFERENCES capture(id) ON DELETE CASCADE
);
"""

CREATE_KANJI_DICT_TABLE = """
CREATE TABLE IF NOT EXISTS kanji_dict (
    kanji TEXT PRIMARY KEY,
    meaning TEXT,
    kunyomi TEXT,
    onyomi TEXT,
    strokes INTEGER,
    jlpt INTEGER,
    grade INTEGER
);
"""

CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);
"""

# All table creation statements in dependency order
ALL_TABLES = [
    CREATE_SCHEMA_VERSION_TABLE,
    CREATE_MEDIA_TABLE,
    CREATE_CAPTURE_TABLE,
    CREATE_CAPTURE_KANJI_TABLE,
    CREATE_KANJI_DICT_TABLE,
]

# ─── Indexes ─────────────────────────────────────────────────────────────────

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_capture_media_id ON capture(media_id);",
    "CREATE INDEX IF NOT EXISTS idx_capture_timestamp ON capture(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_capture_kanji_capture_id ON capture_kanji(capture_id);",
    "CREATE INDEX IF NOT EXISTS idx_capture_kanji_kanji ON capture_kanji(kanji);",
    "CREATE INDEX IF NOT EXISTS idx_kanji_dict_jlpt ON kanji_dict(jlpt);",
]
