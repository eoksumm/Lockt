from db import get_conn
from security import make_key, encrypt_password, decrypt_password

def add_password(user_id, service_name, service_username, password, master_password, salt):
    key = make_key(master_password, salt)
    enc = encrypt_password(password, key)
    conn = get_conn()
    conn.execute(
        'INSERT INTO vault (user_id, service_name, service_username, encrypted_password) VALUES (?, ?, ?, ?)',
        (user_id, service_name, service_username, enc)
    )
    conn.commit()
    conn.close()

def get_passwords(user_id, master_password, salt):
    key = make_key(master_password, salt)
    conn = get_conn()
    rows = conn.execute(
        'SELECT id, service_name, service_username, encrypted_password FROM vault WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    conn.close()
    entries = []
    for row in rows:
        try:
            pw = decrypt_password(row[3], key)
        except Exception:
            pw = '[error]'
        entries.append({'id': row[0], 'service': row[1], 'username': row[2], 'password': pw})
    return entries

def delete_password(entry_id, user_id):
    conn = get_conn()
    conn.execute('DELETE FROM vault WHERE id = ? AND user_id = ?', (entry_id, user_id))
    conn.commit()
    conn.close()
