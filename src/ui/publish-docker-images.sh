#/bin/bash

IMAGE_VERSION="1.0.0"

docker build -f Dockerfile.amd64 -t openrace/ui:$IMAGE_VERSION-amd64 .
docker push openrace/ui:$IMAGE_VERSION-amd64

docker build -f Dockerfile.arm32v7 -t openrace/ui:$IMAGE_VERSION-arm32v7 .
docker push openrace/ui:$IMAGE_VERSION-arm32v7

docker manifest create openrace/ui:$IMAGE_VERSION openrace/ui:$IMAGE_VERSION-amd64 openrace/ui:$IMAGE_VERSION-arm32v7
docker manifest annotate openrace/ui:$IMAGE_VERSION openrace/ui:$IMAGE_VERSION-arm32v7 --os linux --arch arm
docker manifest push openrace/ui:$IMAGE_VERSION --purge
