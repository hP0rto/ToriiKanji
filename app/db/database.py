import sqlite3
import os
import shutil
from utils.paths import DB_PATH, resource_path
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_connection():
    # If DB does not exist in AppData, copy template from resources
    if not os.path.exists(DB_PATH):
        template_db = resource_path('build_assets/database/toriikanji.db')
        print(template_db)
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        shutil.copy2(template_db, DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn