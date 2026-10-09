"""
Media service for ToriiKanji.
Manages media sources (apps/games the user captures from).
"""

from PyQt6.QtCore import QObject, pyqtSignal

from db.repositories.media_repository import MediaRepository


class MediaService(QObject):
    """
    Service for managing media sources.
    Emits 'media_changed' when media are added/removed so the UI can refresh.
    """
    media_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.media_repo = MediaRepository()

    def get_all_media(self):
        """Get all registered media sources."""
        return self.media_repo.get_all()

    def get_or_create_media_id(self, title: str) -> int:
        """
        Get the ID for a media title, creating it if it doesn't exist.
        Emits media_changed when a new media is created.
        """
        normalized_title = title.strip().title()

        media = self.media_repo.get_by_title(normalized_title)
        if media:
            return media['id']
        else:
            new_id = self.media_repo.insert(normalized_title)
            try:
                self.media_changed.emit()
            except Exception:
                pass
            return new_id

    def delete_media(self, media_id):
        """Delete a media source by ID. Emits media_changed."""
        result = self.media_repo.delete(media_id)
        try:
            self.media_changed.emit()
        except Exception:
            pass
        return result

    def get_media_by_id(self, media_id):
        """Get a media source by its ID."""
        return self.media_repo.get_by_id(media_id)
