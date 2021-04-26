#!/usr/bin/env bash
set -e

BUILD_DIR=".github/build"
cd $BUILD_DIR

./terraform destroy -auto-approve
