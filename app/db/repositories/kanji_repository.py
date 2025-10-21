
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
        
    def list_kanjis_with_counts(self, limit=200, order_dir='DESC'):
        # order_dir: 'ASC' | 'DESC' (orders by latest capture timestamp)
        order_dir = (order_dir or 'DESC').upper()
        if order_dir not in ('ASC', 'DESC'):
            order_dir = 'DESC'

        order_clause = f"last_capture {order_dir}"

        with get_connection() as conn:
            cur = conn.cursor()

            cur.execute(f"""
                SELECT
                    *,
                    COUNT(ck.capture_id) AS cnt,
                    MAX(c.timestamp) AS last_capture
                FROM kanji_dict k
                INNER JOIN capture_kanji ck ON ck.kanji = k.kanji
                LEFT JOIN capture c ON c.id = ck.capture_id
                GROUP BY k.kanji
                HAVING COUNT(ck.capture_id) > 0
                ORDER BY {order_clause}
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]

    def list_kanjis_with_counts_by_media(self, media_id, limit=200, order_dir='DESC'):
        order_dir = (order_dir or 'DESC').upper()
        if order_dir not in ('ASC', 'DESC'):
            order_dir = 'DESC'

        order_clause = f"last_capture {order_dir}"

        with get_connection() as conn:
            cur = conn.cursor()
            if media_id is None:
                cur.execute(f"""
                    SELECT
                        *,
                        COUNT(ck.capture_id) AS cnt,
                        MAX(c.timestamp) AS last_capture
                    FROM kanji_dict k
                    INNER JOIN capture_kanji ck ON ck.kanji = k.kanji
                    LEFT JOIN capture c ON c.id = ck.capture_id
                    GROUP BY k.kanji
                    HAVING COUNT(ck.capture_id) > 0
                    ORDER BY {order_clause}
                    LIMIT ?
                """, (limit,))
            elif media_id == -1:
                # kanjis in captures without media
                cur.execute(f"""
                    SELECT
                        *,
                        COUNT(ck.capture_id) AS cnt,
                        MAX(c.timestamp) AS last_capture
                    FROM kanji_dict k
                    INNER JOIN capture_kanji ck ON ck.kanji = k.kanji
                    LEFT JOIN capture c ON c.id = ck.capture_id
                    WHERE c.media_id IS NULL
                    GROUP BY k.kanji
                    HAVING COUNT(ck.capture_id) > 0
                    ORDER BY {order_clause}
                    LIMIT ?
                """, (limit,))
            else:
                cur.execute(f"""
                    SELECT
                        *,
                        COUNT(ck.capture_id) AS cnt,
                        MAX(c.timestamp) AS last_capture
                    FROM kanji_dict k
                    INNER JOIN capture_kanji ck ON ck.kanji = k.kanji
                    LEFT JOIN capture c ON c.id = ck.capture_id
                    WHERE c.media_id = ?
                    GROUP BY k.kanji
                    HAVING COUNT(ck.capture_id) > 0
                    ORDER BY {order_clause}
                    LIMIT ?
                """, (media_id, limit))

            return [dict(row) for row in cur.fetchall()]

    def get_kanji_by_char(self, char):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM kanji_dict WHERE kanji = ?', (char,))
            row = cur.fetchone()
            return dict(row) if row else None