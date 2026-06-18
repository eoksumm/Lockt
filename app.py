from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from db import init_db
from auth import register, login
from vault import add_password, get_passwords, delete_password
import os
import secrets
import string

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
csrf = CSRFProtect(app)

init_db()

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
        if register(username, password):
            flash('Account created! You can log in now.')
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
        flash('Saved.')
        return redirect(url_for('index'))
    return render_template('add.html')

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

if __name__ == '__main__':
    app.run(debug=True)
