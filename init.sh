docker-compose up -d
bash launch/wait-for-mongo.sh
bash launch/getup.sh

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
