from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from db import init_db
from auth import register, login
from vault import add_password, get_passwords, delete_password, get_entry, update_password
import os
import secrets
import string
import hashlib
import urllib.request

app = Flask(__name__)
_key_file = os.path.join(os.path.dirname(__file__), '.secret_key')
if os.path.exists(_key_file):
    with open(_key_file) as _f:
        app.secret_key = _f.read().strip()
else:
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
csrf = CSRFProtect(app)

init_db()

def _check_pwned(password):
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    req = urllib.request.Request(
        f'https://api.pwnedpasswords.com/range/{prefix}',
        headers={'Add-Padding': 'true'}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = resp.read().decode('utf-8')
    for line in body.splitlines():
        h, _, c = line.partition(':')
        if h == suffix:
            return int(c)
    return 0

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    entries = get_passwords(session['user_id'], session['master_password'], session['salt'])
    return render_template('index.html', username=session['username'], entries=entries)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Please fill in all fields.')
            return render_template('register.html')
        if len(password) < 8:
            flash('Master password must be at least 8 characters.')
            return render_template('register.html')
        if register(username, password):
            flash('Account created! You can log in now.', 'ok')
            return redirect(url_for('login_page'))
        flash('That username is already taken.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id, salt = login(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            session['master_password'] = password
            session['salt'] = salt
            return redirect(url_for('index'))
        flash('Wrong username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        service = request.form['service_name'].strip()
        username = request.form['service_username'].strip()
        password = request.form['password']
        if not service or not username or not password:
            flash('All fields are required.')
            return render_template('add.html')
        add_password(session['user_id'], service, username, password,
                     session['master_password'], session['salt'])
        flash('Saved.', 'ok')
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        service = request.form['service_name'].strip()
        username = request.form['service_username'].strip()
        password = request.form['password']
        if not service or not username or not password:
            flash('All fields are required.')
            entry = get_entry(entry_id, session['user_id'], session['master_password'], session['salt'])
            return render_template('edit.html', entry=entry)
        update_password(entry_id, session['user_id'], service, username, password,
                        session['master_password'], session['salt'])
        flash('Updated.', 'ok')
        return redirect(url_for('index'))
    entry = get_entry(entry_id, session['user_id'], session['master_password'], session['salt'])
    if not entry:
        return redirect(url_for('index'))
    return render_template('edit.html', entry=entry)

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    delete_password(entry_id, session['user_id'])
    return redirect(url_for('index'))

@app.route('/generate')
def generate():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    chars = string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{}|;:,.<>?'
    pw = ''.join(secrets.choice(chars) for _ in range(16))
    return render_template('generate.html', new_password=pw)

@app.route('/pwned', methods=['GET', 'POST'])
def pwned():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    count = None
    checked = False
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password:
            try:
                count = _check_pwned(password)
                checked = True
            except Exception:
                flash('Could not reach the HIBP API. Check your connection.')
    return render_template('pwned.html', count=count, checked=checked)

if __name__ == '__main__':
    app.run(debug=True)
