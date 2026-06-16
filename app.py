from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import init_db
from auth import register, login
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html', username=session['username'])

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
        user_id = login(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('index'))
        flash('Wrong username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
