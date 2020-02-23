#!/bin/bash -eux

. /usr/local/tomcat/bin/setenv.sh

DEBUG=${DEBUG:-false}

# wait for postgresql to initialise
/usr/local/tomcat/wait-for-it.sh --timeout=3600 ${ODOO_DB_SERVER}:5432

# run liquibase migrations
sleep 3
/etc/bahmni-erp-connect/run-liquibase.sh

# start tomcat
/usr/local/tomcat/bin/catalina.sh jpda run