#!/bin/bash
# Stop all containers
echo "Stopping all containers..."
docker stop $(docker ps -a -q)
# Delete all containers
echo "Deleting all containers..."
docker rm $(docker ps -a -q)
# Delete all images
echo "Deleting all images..."
docker rmi $(docker images -q)