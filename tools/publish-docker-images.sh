#!/usr/bin/env bash

IMAGE_VERSION="1.0.0"

for service in ui race_core led_control
do
    cat ../src/$service/Dockerfile | sed '/as base/ s/FROM /FROM amd64\//g' | docker build -f - -t openrace/$service:$IMAGE_VERSION-amd64 ../src/$service/
    docker push openrace/$service:$IMAGE_VERSION-amd64

    cat ../src/$service/Dockerfile | sed '/as base/ s/FROM /FROM arm32v7\//g' | docker build -f - -t openrace/$service:$IMAGE_VERSION-arm32v7 ../src/$service/
    docker push openrace/$service:$IMAGE_VERSION-arm32v7

    docker manifest create openrace/$service:$IMAGE_VERSION openrace/$service:$IMAGE_VERSION-amd64 openrace/$service:$IMAGE_VERSION-arm32v7
    docker manifest annotate openrace/$service:$IMAGE_VERSION openrace/$service:$IMAGE_VERSION-arm32v7 --os linux --arch arm
    docker manifest push openrace/$service:$IMAGE_VERSION --purge
done