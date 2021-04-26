#!/usr/bin/env bash

# Read and save the list of services to build
services=""
folders=`ls -d */`
for folder in $folders
do
  service=`echo $folder | sed -e 's/^..\///' -e 's/.$//'`
  case $service in
      sqls|readme|properties)
        ;;
      *)
        services=$service","$services
        ;;
  esac
done
echo "SERVICES=$services" >> $GITHUB_ENV

# Persist GITHUB_ENV vars inherited from previous job
echo "arm64=$arm64" >> $GITHUB_ENV
echo "amd64=$amd64" >> $GITHUB_ENV

echo $GITHUB_ENV
