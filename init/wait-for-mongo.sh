#!/bin/bash

CONTAINER="fisiodesk-mongodb"

echo "Waiting for MongoDB to be healthy..."

while true; do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER 2>/dev/null)

  if [ "$STATUS" == "healthy" ]; then
    echo "MongoDB is healthy!"
    break
  fi

  echo "Current status: $STATUS"
  sleep 2
done
