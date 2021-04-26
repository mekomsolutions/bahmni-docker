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
