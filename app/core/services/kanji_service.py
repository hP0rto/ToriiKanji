from db.repositories.kanji_repository import KanjiRepository


class KanjiService():
    def __init__(self):
        self.kanji_repo = KanjiRepository()

    def get_all_kanjis(self, kanjis):
        return self.kanji_repo.find_many(kanjis)
    
    def get_all_kanji_capture(self, capture_id):
        return self.kanji_repo.find_all_kanjis_capture(capture_id)

    def get_all_user_kanji_with_count(self, order):
        return self.kanji_repo.list_kanjis_with_counts(order_dir=order)

    def get_all_user_kanji_with_count_by_media(self, media_id, order):
        return self.kanji_repo.list_kanjis_with_counts_by_media(media_id, order_dir=order)
    

