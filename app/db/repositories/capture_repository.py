from db.database import get_connection

class CaptureRepository:

    def insert_capture(self, raw_text, image_path, media_id=None):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(''' 
                INSERT INTO capture (raw_text ,image_path,media_id) VALUES (?,?, ?)
            ''', (raw_text, image_path,media_id))
            conn.commit()
            return cur.lastrowid
    
    def insert_capture_kanji(self, capture_id, kanji):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT OR IGNORE INTO capture_kanji (capture_id, kanji) VALUES (?,?)
            ''', (capture_id, kanji))
            
            conn.commit()
            
    def select_captures(self):
        return self.select_captures_ordered('DESC')

    def select_captures_ordered(self, order='DESC'):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM capture ORDER BY timestamp {order}')
            return [dict(row) for row in cur.fetchall()]

    def select_captures_by_media(self, media_id, order='DESC'):
        with get_connection() as conn:
            cur = conn.cursor()
            # media_id None previously meant 'all' in UI; treat explicit sentinel -1 as 'no media'
            if media_id is None:
                cur.execute(f'SELECT * FROM capture ORDER BY timestamp {order}')
            elif media_id == -1:
                # captures without media
                cur.execute(f'SELECT * FROM capture WHERE media_id IS NULL ORDER BY timestamp {order}')
            else:
                cur.execute(f'SELECT * FROM capture WHERE media_id = ? ORDER BY timestamp {order}', (media_id,))

            return [dict(row) for row in cur.fetchall()]

    def get_captures_by_kanji(self, kanji_char, order='DESC'):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT c.* FROM capture c
                JOIN capture_kanji ck ON ck.capture_id = c.id
                WHERE ck.kanji = ?
                ORDER BY c.timestamp {order}
            """, (kanji_char,))
            return [dict(row) for row in cur.fetchall()]
            
    def select_capture_by_id(self, id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM capture WHERE id = ?', (id,))
            return cur.fetchone()
    
    def delete_capture(self,id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM capture_kanji WHERE capture_id = ?', (id,))
            cur.execute('DELETE FROM capture WHERE id = ?', (id,))
            conn.commit()
            return cur.rowcount > 0
        
    def update_media_id(self, capture_id, media_id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('UPDATE capture SET media_id = ? WHERE id = ?', (media_id, capture_id))
            conn.commit()