#!/usr/bin/env bash

set -e

IMAGE_VERSION="1.0.3"

for SERVICE in race_core led_control audio_output ui
do
    cat ../src/${SERVICE}/Dockerfile | sed '/as base/ s/FROM /FROM amd64\//g' | docker buildx build --platform linux/amd64 -f - -t docker.io/openrace/${SERVICE}:${IMAGE_VERSION}-amd64 ../src/${SERVICE}/
    docker push docker.io/openrace/${SERVICE}:${IMAGE_VERSION}-amd64

    cat ../src/${SERVICE}/Dockerfile | sed '/as base/ s/FROM /FROM arm32v7\//g' | docker buildx build --platform linux/arm/v7 -f - -t docker.io/openrace/${SERVICE}:${IMAGE_VERSION}-arm32v7 ../src/${SERVICE}/
    docker push docker.io/openrace/${SERVICE}:${IMAGE_VERSION}-arm32v7
done
