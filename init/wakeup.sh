# sudo ss -ltnp | grep 27017
# sudo kill -9 $PID

docker-compose down -v --remove-orphans
docker network prune -f
#docker-compose up -d
