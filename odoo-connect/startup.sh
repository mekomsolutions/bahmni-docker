#!/bin/bash -eux

. /usr/local/tomcat/bin/setenv.sh

DEBUG=${DEBUG:-false}
DEBUG_PORT=${DEBUG_PORT:-8000}
catalina_params=()

# wait for postgresql to initialise
/usr/local/tomcat/wait-for-it.sh --timeout=3600 ${ODOO_DB_SERVER}:5432

# run liquibase migrations
sleep 3
/etc/bahmni-erp-connect/run-liquibase.sh

if [ $DEBUG == true ]; then
    export JPDA_ADDRESS=$DEBUG_PORT
    export JPDA_TRANSPORT=dt_socket
    catalina_params+=(jpda)
fi
catalina_params+=(run)

# start tomcat
/usr/local/tomcat/bin/catalina.sh "${catalina_params[@]}"