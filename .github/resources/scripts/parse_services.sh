#!/usr/bin/env bash
set -e

# Read and save the list of services to build
echo "🔍 Reading through the directories to construct the list of services..."
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

echo "Services to be built: " $services
echo "::set-output name=services::$services"
