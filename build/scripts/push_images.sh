#!/usr/bin/env bash
WORKDIR=$PWD/workdir
REPO_DIR=$PWD
BUILD_DIR=$REPO_DIR/build
services=$SERVICES

echo "📑 Services to push: "
echo $services

echo "⚙️ Set the Revision:"
REVISION=$(git rev-parse --short HEAD)

DOCKER_USERNAME=mekomsolutions

echo "⚙️ Run Docker build commands on remotes..."
archs=arm64 amd64
for arch in archs
do
  ip=${!arch}
  echo "Remote: $arch: $ip"

  echo "🔑 Log in Docker Hub"
  ssh -t -o StrictHostKeyChecking=no -i $AWS_AMI_PRIVATE_KEY_FILE -p 22 ubuntu@$ip /bin/bash -x << EOF
    sudo docker login -p $DOCKER_PASSWORD -u $DOCKER_USERNAME
  EOF

  echo "⚙️ Run Docker push commands on remote."
  ssh -t -o StrictHostKeyChecking=no -i $AWS_AMI_PRIVATE_KEY_FILE -p 22 ubuntu@$ip /bin/bash -x << EOF
    cd bahmni-docker/
    services=$services
    echo "⚙️ Will push the following list of services:" $services
    for service in \${services//,/ }
    do
        echo "⚙️ Pushing '$DOCKER_USERNAME/\${service}:${REVISION}_$arch'..."
        sudo docker push $DOCKER_USERNAME/\${service}:${REVISION}_$arch
        echo "⚙️ Create manifest '$DOCKER_USERNAME/\${service}:${REVISION}_$arch'..."
        docker manifest create $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD) --amend $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)_arm64 --amend $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)_amd64
        docker manifest push $DOCKER_USERNAME/${service}:$(git rev-parse --short HEAD)
        docker manifest push $DOCKER_USERNAME/${service}:latest
    done
  EOF

done
