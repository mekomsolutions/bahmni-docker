#!/usr/bin/env bash
set -e

BUILD_DIR=".github/resources"
cd $BUILD_DIR

./terraform destroy -auto-approve
