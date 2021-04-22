#!/usr/bin/env bash -e
WORKDIR=$PWD/workdir
REPO_DIR=$PWD/..

export TF_VAR_aws_api_key='${{ secrets.AWS_API_KEY_1 }}'
export TF_VAR_aws_api_secret='${{ secrets.AWS_API_SECRET_1 }}'

#wget https://releases.hashicorp.com/terraform/0.13.0/terraform_0.13.0_linux_amd64.zip -O $WORKDIR/terraform.zip
#wget https://releases.hashicorp.com/terraform/0.13.0/terraform_0.13.0_darwin_amd64.zip -O $WORKDIR/terraform.zip
#unzip $WORKDIR/terraform.zip
chmod +x ./terraform
./terraform version
./terraform init
./terraform fmt
./terraform validate
./terraform apply -auto-approve

ip=$(cat $PWD/terraform.tfstate | jq -r .outputs.arm_builder_stats.value.ip)
echo "☑️ AWS instance started. IP=$ip"
# Set SSH vars
TEMPFILE=$(mktemp)
echo "${{ secrets.AWS_AMI_PRIVATE_KEY }}" > certs/deploy.key
ssh_params=" -o 'UserKnownHostsFile $TEMPFILE' -i certs/deploy.key -p 22"
server="ubuntu@$ip"

# Save the public key
server_public_key=$(cat $PWD/terraform.tfstate | jq -r '.resources[] | select(.name == "host-rsa") | .instances[].attributes.public_key_openssh')
echo "$ip $server_public_key" >> $TEMPFILE

# Read and save the list of services to build
services=""
folders=`ls -d ../*/`
for folder in $folders
do
  service=`echo $folder | sed -e 's/^..\///' -e 's/.$//'`
  case $service in
      sqls|readme|properties)
        ;;
      *)
        services=$service"\n"$services
        ;;
  esac
done
echo -e $services > $REPO_DIR/services.txt
echo -e "📑 List of services to build: "
cat $REPO_DIR/services.txt

# Set the Git revision
rm -f $REPO_DIR/vars.env
echo "REVISION"=$(git rev-parse --short HEAD) >> $REPO_DIR/vars.env

# Set the CPU arch
echo "CPU_ARCH=arm64" >> $REPO_DIR/vars.env

# Set the Docker creds
echo "DOCKER_USERNAME=mekomsolutions" >> $REPO_DIR/vars.env
echo "DOCKER_PASSWORD=${{ mekomsolutionsDOCKER_HUB_REGISTRY_PASSWORD }}" >> $REPO_DIR/vars.env

# Send the project to remote
ssh -o "UserKnownHostsFile $TEMPFILE" -i certs/deploy.key -p 22 ubuntu@$ip "mkdir -p /home/ubuntu/bahmni-docker"
rsync -av -e "ssh $ssh_params" ../ $server:/home/ubuntu/bahmni-docker/ --exclude .git --exclude build
ssh -o "UserKnownHostsFile $TEMPFILE" -i certs/deploy.key -p 22 ubuntu@$ip /bin/bash -x << 'EOF'

cd bahmni-docker/
source vars.env

services=$(cat services.txt)
echo $services
for service in ${services}
do
    echo "⚙️ Building '$service' ($CPU_ARCH) image"
    docker build ${service}/ -t $DOCKER_USERNAME/${service}:${REVISION}_${CPU_ARCH}
done
EOF

./terraform destroy -auto-approve
