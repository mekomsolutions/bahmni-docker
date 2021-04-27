#!/usr/bin/env bash
set -e

BUILD_DIR=".github/resources"
mkdir -p $BUILD_DIR
cd $BUILD_DIR

./terraform destroy -auto-approve
