from db import get_conn
from security import hash_password, check_password
import sqlite3

def register(username, password):
    conn = get_conn()
    try:
        conn.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login(username, password):
    conn = get_conn()
    row = conn.execute(
        'SELECT id, password_hash FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    if row and check_password(password, row[1]):
        return row[0]
    return None
