#!/usr/bin/env bash
WORKDIR=$PWD/workdir
REPO_DIR=$PWD
BUILD_DIR=$REPO_DIR/build
services=$SERVICES

echo "📑 Services to build: "
echo $services

echo "⚙️ Set the Revision and CPU architecture:"
REVISION=$(git rev-parse --short HEAD)
CPU_ARCH=arm64

# Set the Docker creds
DOCKER_USERNAME=mekomsolutions
DOCKER_PASSWORD=${{ secrets.DOCKER_HUB_REGISTRY_PASSWORD }}

echo "⚙️ Set AWS AMI private key."
AWS_AMI_PRIVATE_KEY_FILE=$(mktemp)
echo "${{ secrets.AWS_AMI_PRIVATE_KEY }}" > $AWS_AMI_PRIVATE_KEY_FILE
chmod 600 $AWS_AMI_PRIVATE_KEY_FILE

echo "⚙️ Run Docker build commands on remotes..."
IPs=$arm64 $amd64
for ip in $IPs
do
  echo "Remote: $ip"
  ssh -t -o StrictHostKeyChecking=no -i $AWS_AMI_PRIVATE_KEY_FILE -p 22 ubuntu@$ip /bin/bash -x << EOF
    cd bahmni-docker/
    services=$services
    echo "⚙️ Will build the following list of services:" $services
    for service in \${services//,/ }
    do
        echo "⚙️ Build '\${service}' image and tag it as '$DOCKER_USERNAME/\${service}:${REVISION}_$arch'..."
        sudo docker build \${service}/ -t $DOCKER_USERNAME/\${service}:${REVISION}_${CPU_ARCH}
    done
  EOF
done
