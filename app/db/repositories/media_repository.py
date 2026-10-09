"""
Media repository for ToriiKanji.
Handles all database operations for the 'media' table.
"""

from db.database import get_connection


class MediaRepository:
    def get_all(self):
        """Get all registered media sources, ordered by title."""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM media ORDER BY title ASC')
            return cur.fetchall()

    def get_by_id(self, media_id):
        """Get a media record by its ID."""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM media WHERE id = ?', (media_id,))
            return cur.fetchone()

    def get_by_title(self, title):
        """Get a media record by its title."""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM media WHERE title = ?', (title,))
            return cur.fetchone()

    def insert(self, title):
        """Insert a new media record and return its ID."""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO media (title) VALUES (?)', (title,))
            conn.commit()
            return cur.lastrowid

    def delete(self, media_id):
        """Delete a media record. Unlinks associated captures first."""
        with get_connection() as conn:
            cur = conn.cursor()
            # Unlink captures before deleting to avoid orphaned references
            cur.execute('UPDATE capture SET media_id = NULL WHERE media_id = ?', (media_id,))
            cur.execute('DELETE FROM media WHERE id = ?', (media_id,))
            conn.commit()
