from db import get_conn
from security import hash_password, check_password
import sqlite3
import os
import base64

def register(username, password):
    salt = base64.b64encode(os.urandom(16)).decode()
    conn = get_conn()
    try:
        conn.execute(
            'INSERT INTO users (username, password_hash, encryption_salt) VALUES (?, ?, ?)',
            (username, hash_password(password), salt)
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
        'SELECT id, password_hash, encryption_salt FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()
    if row and check_password(password, row[1]):
        return row[0], row[2]
    return None, None
