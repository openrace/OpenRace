#!/usr/bin/env bash

IMAGE_VERSION="1.0.1"

for SERVICE in ui race_core led_control
do
    cat ../src/${SERVICE}/Dockerfile | sed '/as base/ s/FROM /FROM amd64\//g' | docker build -f - -t openrace/${SERVICE}:${IMAGE_VERSION}-amd64 ../src/${SERVICE}/
    docker push openrace/${SERVICE}:${IMAGE_VERSION}-amd64

    # https://github.com/gliderlabs/docker-alpine/issues/298
    # https://github.com/gliderlabs/docker-alpine/pull/484
    # thanks alpine linux for arm32v6 -.-
    cat ../src/${SERVICE}/Dockerfile | sed '/as base/ s/FROM /FROM arm32v6\//g' | docker build -f - -t openrace/${SERVICE}:${IMAGE_VERSION}-arm32v7 ../src/${SERVICE}/
    docker push openrace/${SERVICE}:${IMAGE_VERSION}-arm32v7

    docker manifest create openrace/${SERVICE}:${IMAGE_VERSION} openrace/${SERVICE}:${IMAGE_VERSION}-amd64 openrace/${SERVICE}:${IMAGE_VERSION}-arm32v7

    docker manifest annotate openrace/${SERVICE}:${IMAGE_VERSION} openrace/${SERVICE}:${IMAGE_VERSION}-amd64 --os linux --arch amd64
    docker manifest annotate openrace/${SERVICE}:${IMAGE_VERSION} openrace/${SERVICE}:${IMAGE_VERSION}-arm32v7 --os linux --arch arm --variant v7

    docker manifest push openrace/${SERVICE}:${IMAGE_VERSION} --purge
done