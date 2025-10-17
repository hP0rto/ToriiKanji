
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

    def list_kanjis_with_counts(self, limit=200, order_by='count'):
        order_clause = 'COUNT(ck.capture_id) DESC' if order_by == 'count' else 'k.kanji ASC'
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT k.kanji, COUNT(ck.capture_id) as cnt, k.jlpt, k.strokes
                FROM kanji_dict k
                LEFT JOIN capture_kanji ck ON ck.kanji = k.kanji
                GROUP BY k.kanji
                ORDER BY {order_clause}
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]

    def get_kanji_by_char(self, char):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM kanji_dict WHERE kanji = ?', (char,))
            row = cur.fetchone()
            return dict(row) if row else None