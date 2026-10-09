"""
Kanji service for ToriiKanji.
Provides kanji dictionary lookups and user kanji statistics.
"""

from db.repositories.kanji_repository import KanjiRepository


class KanjiService:
    def __init__(self):
        self.kanji_repo = KanjiRepository()

    def get_all_kanjis(self, kanjis):
        """Look up multiple kanji characters in the dictionary."""
        return self.kanji_repo.find_many(kanjis)

    def get_all_kanji_capture(self, capture_id):
        """Get all kanji associated with a specific capture."""
        return self.kanji_repo.find_all_kanjis_capture(capture_id)

    def get_all_user_kanji_with_count(self, order):
        """Get all user's kanji with occurrence counts."""
        return self.kanji_repo.list_kanjis_with_counts(order_dir=order)

    def get_all_user_kanji_with_count_by_media(self, media_id, order):
        """Get user's kanji with counts filtered by media source."""
        return self.kanji_repo.list_kanjis_with_counts_by_media(media_id, order_dir=order)
