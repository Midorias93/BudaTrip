#!/bin/bash

brew update

python3 -m venv .venv

source .venv/bin/activate

pip install update pip

cd backend

pip install -r requirement.txt

docker compose up -d

python3 app.py &

ngrok http 8000


