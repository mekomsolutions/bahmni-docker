#!/usr/bin/env bash
WORKDIR=$PWD/workdir
REPO_DIR=$PWD
BUILD_DIR=$REPO_DIR/build

cd $BUILD_DIR

./terraform destroy -auto-approve
