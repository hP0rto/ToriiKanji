from db.repositories.media_repository import MediaRepository

class MediaService:
    def __init__(self):
        self.media_repo = MediaRepository()

    def get_all_media(self):
        return self.media_repo.get_all()

    def get_or_create_media_id(self, title: str) -> int:
        """
        Recebe um título. Se já existir, retorna o ID.
        Se não, cria um novo e retorna o novo ID.
        """
        # Normaliza o input para evitar duplicatas (ex: "chrome" vs "Chrome")
        normalized_title = title.strip().title()

        media = self.media_repo.get_by_title(normalized_title)
        if media:
            return media['id']
        else:
            return self.media_repo.insert(normalized_title)
            
    def delete_media(self, media_id):
        return self.media_repo.delete(media_id)
    
    def get_media_by_id(self, media_id):
        return self.media_repo.get_by_id(media_id)