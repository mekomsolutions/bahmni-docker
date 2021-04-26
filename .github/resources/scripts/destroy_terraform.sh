#!/usr/bin/env bash -e

BUILD_DIR=".github/build"
cd $BUILD_DIR

./terraform destroy -auto-approve
