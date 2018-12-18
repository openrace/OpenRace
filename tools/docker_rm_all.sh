#!/usr/bin/env bash

echo "Stopping all containers..."
docker stop $(docker ps -a -q)

echo "Deleting all containers..."
docker rm $(docker ps -a -q)

echo "Deleting all images..."
docker rmi $(docker images -q)
