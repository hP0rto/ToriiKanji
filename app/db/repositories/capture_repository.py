from db.database import get_connection

class CaptureRepository:

    def insert_capture(self, image_path, media_id=None):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(''' 
                INSERT INTO capture (image_path,media_id) VALUES (?, ?)
            ''', (image_path,media_id))
            conn.commit()
            return cur.lastrowid
    
    def insert_capture_kanji(self, capture_id, kanji):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT OR IGNORE INTO capture_kanji (capture_id, kanji) VALUES (?,?)
            ''', (capture_id, kanji))
            
            conn.commit()