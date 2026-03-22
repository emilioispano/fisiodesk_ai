docker-compose up -d
bash launch/wait-for-mongo.sh
bash launch/getup.sh
python3 -m app.main
