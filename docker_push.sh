#!/bin/bash

Services=odoo,appointments,bahmni-mart,bahmni-reports,bahmniapps,implementer-interface,metabase,odoo-connect,openmrs,openelis

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

for service in ${Services//,/ }
do
    echo "creating manifest for $service"
    docker manifest create $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD) --amend $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)_arm64 --amend $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)_amd64
    docker manifest create $DOCKER_USERNAME/${service}:latest --amend $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)_arm64 --amend $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)_amd64
    docker manifest push $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)
    docker manifest push $DOCKER_USERNAME/${service}:latest
done
