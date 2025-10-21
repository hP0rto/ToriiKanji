from db.repositories.media_repository import MediaRepository
from PyQt6.QtCore import QObject, pyqtSignal


class MediaService(QObject):
    """Service managing medias. Emits `media_changed` when medias are added/removed so UI can refresh."""
    media_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.media_repo = MediaRepository()

    def get_all_media(self):
        return self.media_repo.get_all()

    def get_or_create_media_id(self, title: str) -> int:
        """
        Receive a title. If exists, return id, otherwise insert and return new id.
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
        result = self.media_repo.delete(media_id)
        try:
            self.media_changed.emit()
        except Exception:
            pass
        return result
    
    def get_media_by_id(self, media_id):
        return self.media_repo.get_by_id(media_id)