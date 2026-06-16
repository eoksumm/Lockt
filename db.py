import sqlite3
import os

DB = 'lockt.db'

def init_db():
    if os.path.exists(DB):
        return
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB)
