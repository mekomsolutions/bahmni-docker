#!/bin/bash -eux

DEBUG=${DEBUG:-false}

# wait for postgresql to initialise
/usr/local/tomcat/wait-for-it.sh --timeout=3600 ${ODOO_DB_SERVER}:5432


if [ $DEBUG ]; then
    export JPDA_ADDRESS="1044"
    export JPDA_TRANSPORT=dt_socket
fi


# start tomcat
/usr/local/tomcat/bin/catalina.sh jpda run &

# run liquibase migrations
sleep 3
/etc/bahmni-erp-connect/run-liquibase.sh

# bring tomcat process to foreground again
wait ${!}