#!/usr/bin/env bash
WORKDIR=$PWD/workdir
REPO_DIR=$PWD
BUILD_DIR=$REPO_DIR/build

cd $BUILD_DIR
export TF_VAR_aws_api_key='${{ secrets.AWS_API_KEY_1 }}'
export TF_VAR_aws_api_secret='${{ secrets.AWS_API_SECRET_1 }}'

wget https://releases.hashicorp.com/terraform/0.13.0/terraform_0.13.0_linux_amd64.zip -O terraform.zip
unzip terraform.zip
chmod +x ./terraform
./terraform version
./terraform init
./terraform fmt
./terraform validate
./terraform apply -auto-approve

arm64_ip=$(cat $PWD/terraform.tfstate | jq -r .outputs.arm64_builder_stats.value.ip)
amd64_ip=$(cat $PWD/terraform.tfstate | jq -r .outputs.amd64_builder_stats.value.ip)
echo "☑️ AWS instance started. ARM64 instance IP: $arm64_ip, AMD64 instance IP: $amd64_ip"
echo "arm64=$arm64_ip" >> $GITHUB_ENV
echo "amd64=$amd64_ip" >> $GITHUB_ENV
