#!/bin/bash

if ! command -v python3 &> /dev/null; then
    echo "python3 not found. Please install it first."
    exit 1
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt

echo ""
echo "Done. To start:"
echo "  source venv/bin/activate"
echo "  python app.py"
