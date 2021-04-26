#!/usr/bin/env bash
WORKDIR=$PWD/workdir
REPO_DIR=$PWD
BUILD_DIR=$REPO_DIR/build
services=$SERVICES

echo "📑 Services to build: "
echo $services

echo "⚙️ Set the Revision:"
REVISION=$(git rev-parse --short HEAD)

DOCKER_USERNAME=mekomsolutions

echo "⚙️ Run Docker build commands on remotes..."
archs=arm64,amd64
for arch in ${archs//,/ }
do
  ip=${!arch}
  echo "Remote: $arch: $ip"

  ssh -t -o StrictHostKeyChecking=no -i $AWS_AMI_PRIVATE_KEY_FILE -p 22 ubuntu@$ip /bin/bash -x << EOF
    cd bahmni-docker/
    services=$services
    echo "⚙️ Will build the following list of services:" $services
    for service in \${services//,/ }
    do
        echo "⚙️ Build '\${service}' image and tag it as '$DOCKER_USERNAME/\${service}:${REVISION}_$arch'..."
        sudo docker build \${service}/ -t $DOCKER_USERNAME/\${service}:${REVISION}_${arch}
    done
  EOF
done
