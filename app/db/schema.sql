CREATE TABLE kanji_dict (
    kanji TEXT PRIMARY KEY,
    onyomi TEXT,
    kunyomi TEXT,
    meaning TEXT,
    grade INTEGER,
    jlpt INTEGER
);

CREATE TABLE media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT
);

CREATE TABLE capture (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    media_id INTEGER,
    FOREIGN KEY (media_id) REFERENCES media(id)
);

CREATE TABLE capture_kanji (
    capture_id INTEGER,
    kanji TEXT,
    PRIMARY KEY (capture_id, kanji),
    FOREIGN KEY (capture_id) REFERENCES capture(id),
    FOREIGN KEY (kanji) REFERENCES kanji_dict(kanji)
);