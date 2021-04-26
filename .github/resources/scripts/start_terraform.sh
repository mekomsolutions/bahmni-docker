#!/usr/bin/env bash
set -e

BUILD_DIR=".github/build"
mkdir $BUILD_DIR && cd $BUILD_DIR/

echo AWS_API_KEY_1="$TF_VAR_aws_api_key"

wget https://releases.hashicorp.com/terraform/0.13.0/terraform_0.13.0_linux_amd64.zip -O terraform.zip
unzip terraform.zip
chmod +x ./terraform
./terraform version
./terraform init
./terraform fmt
./terraform validate
./terraform apply -auto-approve

arm64_ip=$(cat $BUILD_DIR/terraform.tfstate | jq -r .outputs.arm64_builder_stats.value.ip)
amd64_ip=$(cat $BUILD_DIR/terraform.tfstate | jq -r .outputs.amd64_builder_stats.value.ip)

echo "☑️ AWS instance started. ARM64 instance IP: $arm64_ip, AMD64 instance IP: $amd64_ip"
echo "arm64=$arm64_ip" >> $GITHUB_ENV
echo "amd64=$amd64_ip" >> $GITHUB_ENV
