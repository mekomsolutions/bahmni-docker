#!/usr/bin/env bash
set -e
services=$SERVICES

echo "📑 "
echo $services

REVISION=$(git rev-parse --short HEAD)

DOCKER_USERNAME=mekomsolutions

# Build the docker manifests commands
archs=arm64,amd64
args=" "
for arch in ${archs//,/ }
do
  args="${args} --amend $DOCKER_USERNAME/\\\${service}:${REVISION}_${arch}"
done
echo "$args"

# Log in one of the machines
echo "⚙️ "
arch=arm64

ip=${!arch}
echo "Remote: $arch: $ip"

echo "🔑 Log in Docker Hub"
ssh -t -o StrictHostKeyChecking=no -i $AWS_AMI_PRIVATE_KEY_FILE -p 22 ubuntu@$ip /bin/bash -e << EOF
sudo docker login -p $DOCKER_PASSWORD -u $DOCKER_USERNAME
EOF

echo "⚙️ "
ssh -t -o StrictHostKeyChecking=no -i $AWS_AMI_PRIVATE_KEY_FILE -p 22 ubuntu@$ip /bin/bash -e << EOF
cd bahmni-docker/
services=$services
echo "⚙️ Will push the following list of services:" $services
for service in \${services//,/ }
do
    set -x
    echo "⚙️ Create manifest '$DOCKER_USERNAME/\${service}:${REVISION}'..."
    echo "sudo docker manifest create $DOCKER_USERNAME/\${service}:${REVISION} ${args}"
    sudo docker manifest create $DOCKER_USERNAME/\${service}:${REVISION} ${args}
    sudo docker manifest push $DOCKER_USERNAME/\${service}:${REVISION}

    echo "⚙️ Create manifest '$DOCKER_USERNAME/\${service}:latest'..."
    sudo docker manifest create $DOCKER_USERNAME/\${service}:latest ${args}
    sudo docker manifest push $DOCKER_USERNAME/\${service}:latest
done
EOF

done
