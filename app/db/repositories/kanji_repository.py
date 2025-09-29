
from db.database import get_connection

class KanjiRepository:

    def find_many(self, kanjis):
        with get_connection() as conn:
            query = "SELECT * FROM kanji_dict WHERE kanji IN ({})".format(
                ",".join("?" for _ in kanjis)
            )
            cur = conn.cursor()
            cur.execute(query, kanjis)
            return [dict(row) for row in cur.fetchall()]
        
    def find_all_kanjis_capture(self, capture_id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT kanji FROM capture_kanji WHERE capture_id = ?', (capture_id,))
            
            kanjis = [row['kanji'] for row in cur.fetchall()]
            
            return self.find_many(kanjis)