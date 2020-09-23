#!/bin/bash
echo fine
Services=odoo,appointments,bahmni-mart,bahmni-reports,bahmniapps,implementer-interface,metabase,odoo-connect,openmrs

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

for service in ${Services//,/ }
do
    echo "Building $service $TRAVIS_CPU_ARCH image"
    docker build ${service}/ -t $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)_$TRAVIS_CPU_ARCH
    echo "Pushing $service $TRAVIS_CPU_ARCH image"
    docker push $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)_$TRAVIS_CPU_ARCH
done
