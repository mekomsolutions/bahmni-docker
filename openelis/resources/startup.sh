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

# wait for mysql to initialise
/usr/local/tomcat/wait-for-it.sh --timeout=3600 ${OPENMRS_DB_SERVER}:3306

sleep 30

/bin/bash /opt/liquibase/db_migrate.sh

/bin/bash catalina.sh run
