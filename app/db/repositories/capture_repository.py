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
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM capture')
            return [dict(row) for row in cur.fetchall()]
            
    def select_capture_by_id(self, id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM capture WHERE id = ?', (id,))
            return cur.fetchone()
    
    def delete_capture(self,id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM capture WHERE id = ?', (id,))
            return cur.fetchone()