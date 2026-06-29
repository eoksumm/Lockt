# Lockt

A local secure password manager built with Flask.

## Features

- Register and log in with a master password
- Add, edit, view, and delete saved passwords
- Passwords stored encrypted (AES via Fernet + PBKDF2 key derivation)
- Show/hide toggle and copy-to-clipboard on every vault entry
- Built-in password generator
- Password strength meter on registration
- Have I Been Pwned breach check (k-anonymity, no password ever sent)
- CSRF protection on all forms

## Setup

```bash
bash setup.sh
source venv/bin/activate
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## How encryption works

When you register, a random 16-byte salt is generated for your account. Every time you log in, your master password and that salt are run through PBKDF2 (100,000 iterations, SHA-256) to derive an AES encryption key. That key is used to encrypt and decrypt your vault entries via Fernet. The key is never stored — it lives in the session only while you're logged in.

## Project structure

```
app.py          Flask routes
auth.py         Register and login logic
vault.py        Add, get, delete vault entries
security.py     Password hashing (bcrypt) and encryption (Fernet/PBKDF2)
db.py           Database setup
templates/      HTML pages
static/         Icons
```

## Dependencies

- Flask, Flask-WTF
- bcrypt
- cryptography
