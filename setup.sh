#!/bin/bash

if ! command -v python3 &> /dev/null; then
    echo "python3 not found. Please install it first."
    exit 1
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt
python3 -c "from db import init_db; init_db()"

if [ ! -f .secret_key ]; then
    python3 -c "import secrets; print(secrets.token_hex(32))" > .secret_key
fi

echo ""
echo "Done. To start:"
echo "  source venv/bin/activate"
echo "  python app.py"
