"""Repository layer: one class per table group, all built on db.database.get_connection."""

from db.repositories.capture_repository import CaptureRepository
from db.repositories.kanji_repository import KanjiRepository
from db.repositories.media_repository import MediaRepository

__all__ = ["CaptureRepository", "KanjiRepository", "MediaRepository"]
