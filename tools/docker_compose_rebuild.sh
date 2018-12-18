#!/usr/bin/env bash

echo "Fetching newest image versions"
docker-compose pull

echo "Removing all containers (stopped and running)"
docker-compose rm -f

echo "Rebuilding all containers"
docker-compose up --build
