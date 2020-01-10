#!/usr/bin/env bash

set -e

IMAGE_VERSION="1.0.2"

for SERVICE in ui race_core led_control audio_output
do
    cat ../src/${SERVICE}/Dockerfile | sed '/as base/ s/FROM /FROM amd64\//g' | docker build -f - -t openrace/${SERVICE}:${IMAGE_VERSION}-amd64 ../src/${SERVICE}/
    docker push openrace/${SERVICE}:${IMAGE_VERSION}-amd64

    # https://github.com/gliderlabs/docker-alpine/issues/298
    # https://github.com/gliderlabs/docker-alpine/pull/484
    # thanks alpine linux for arm32v6 -.-
    cat ../src/${SERVICE}/Dockerfile | sed '/as base/ s/FROM /FROM arm32v7\//g' | docker build -f - -t openrace/${SERVICE}:${IMAGE_VERSION}-arm32v7 ../src/${SERVICE}/
    docker push openrace/${SERVICE}:${IMAGE_VERSION}-arm32v7
done
