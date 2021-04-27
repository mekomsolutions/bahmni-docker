#!/usr/bin/env bash
set -e
services=$SERVICES

echo "📑 Services to push: "
echo $services

REVISION="85e000c"

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
  echo "⚙️ Pushing images for the following list of services:" $services
  for service in \${services//,/ }
  do
      echo "⚙️ Pushing '$DOCKER_USERNAME/\${service}:${REVISION}_$arch'..."
      sudo docker push $DOCKER_USERNAME/\${service}:${REVISION}_$arch
  done
EOF

done
