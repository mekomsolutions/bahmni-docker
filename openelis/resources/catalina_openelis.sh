#!/bin/sh
set -e -x
/bin/bash /usr/local/tomcat/bin/setenv.sh

mkdir -p /usr/local/tomcat/.OpenELIS

configFiles=`ls -d /etc/properties/*`
for file in $configFiles
do
    name=$(basename "${file}")
    envsubst < ${file} > /usr/local/tomcat/.OpenELIS/${name}
done

/bin/bash catalina.sh run
