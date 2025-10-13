from db.database import get_connection

class MediaRepository:
    def get_all(self):
        """ Retorna todas as mídias cadastradas. """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM media ORDER BY title ASC')
            return cur.fetchall()
    def get_by_id(self, id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM media WHERE id = ?', (id, ))
            return cur.fetchone()

    def get_by_title(self, title):
        """ Busca uma mídia pelo título. """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM media WHERE title = ?', (title,))
            return cur.fetchone()

    def insert(self, title):
        """ Insere uma nova mídia e retorna seu ID. """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO media (title) VALUES (?)', (title,))
            conn.commit()
            return cur.lastrowid
    def delete(self, media_id):
        """ Deleta uma mídia pelo seu ID. """
        with get_connection() as conn:
            cur = conn.cursor()
            # Opcional: Desvincular capturas antes de deletar para evitar erros
            cur.execute('UPDATE capture SET media_id = NULL WHERE media_id = ?', (media_id,))
            cur.execute('DELETE FROM media WHERE id = ?', (media_id,))
            conn.commit()