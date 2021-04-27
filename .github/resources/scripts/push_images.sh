#!/usr/bin/env bash
set -e
services=$SERVICES

echo "📑 Services to push: "
echo $services

REVISION=$(git rev-parse --short HEAD)

DOCKER_USERNAME=mekomsolutions

echo "⚙️ Run Docker build commands on remotes..."
archs=arm64,amd64
for arch in ${archs//,/ }
do
  ip=${!arch}
  echo "Remote: $arch: $ip"

  echo "🔑 Log in Docker Hub"
  ssh -t -o StrictHostKeyChecking=no -i $AWS_AMI_PRIVATE_KEY_FILE -p 22 ubuntu@$ip /bin/bash -e << EOF
  sudo docker login -p $DOCKER_PASSWORD -u $DOCKER_USERNAME
EOF

echo "⚙️ Run Docker push commands on remote."
ssh -t -o StrictHostKeyChecking=no -i $AWS_AMI_PRIVATE_KEY_FILE -p 22 ubuntu@$ip /bin/bash -e << EOF
  cd bahmni-docker/
  services=$services
  echo "⚙️ Will push the following list of services:" $services
  for service in \${services//,/ }
  do
      echo "⚙️ Pushing '$DOCKER_USERNAME/\${service}:${REVISION}_$arch'..."
      sudo docker push $DOCKER_USERNAME/\${service}:${REVISION}_$arch

      echo "⚙️ Create manifest '$DOCKER_USERNAME/\${service}:${REVISION}'..."
      sudo docker manifest create $DOCKER_USERNAME/\${service}:${REVISION} --amend $DOCKER_USERNAME/\${service}:${REVISION}_${arch}
      sudo docker manifest push $DOCKER_USERNAME/\${service}:${REVISION}

      echo "⚙️ Create manifest '$DOCKER_USERNAME/\${service}:latest'..."
      sudo docker manifest create $DOCKER_USERNAME/\${service}:latest --amend $DOCKER_USERNAME/\${service}:${REVISION}_${arch}
      sudo docker manifest push $DOCKER_USERNAME/\${service}:latest
  done
EOF

done
