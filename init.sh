#!/bin/bash

set -e

echo "Composing..."
docker-compose up -d
bash init/wait-for-mongo.sh
bash init/getup.sh

echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependancies..."
pip install --upgrade pip
pip install -r requirements.txt
