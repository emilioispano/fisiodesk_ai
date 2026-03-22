docker-compose up -d
bash init/wait-for-mongo.sh
bash init/getup.sh

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
