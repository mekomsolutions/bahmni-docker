#!/bin/sh
set -e -x

if [ -f /etc/bahmni-erp-connect/bahmni-erp-connect.conf ]; then
. /etc/bahmni-erp-connect/bahmni-erp-connect.conf
fi

if [ -f /etc/bahmni-installer/bahmni.conf ]; then
. /etc/bahmni-installer/bahmni.conf
fi

# WEBAPP_PATH=${WEBAPP_PATH:-/opt/bahmni-erp-connect/}
ODOO_DB=${ODOO_DB:-bahmni}
ODOO_DB_SERVER=${ODOO_DB_SERVER:-odoo-postgresql}
ODOO_DB_USERNAME=${ODOO_DB_USERNAME:-odoo}
ODOO_DB_PASSWORD=${ODOO_DB_PASSWORD:-odoo}

CHANGE_LOG_TABLE="-Dliquibase.databaseChangeLogTableName=liquibasechangelog -Dliquibase.databaseChangeLogLockTableName=liquibasechangeloglock"
LIQUIBASE_JAR="/etc/liquibase-core-2.0.3.jar"
DRIVER="org.postgresql.Driver"
CREDS="--url=jdbc:postgresql://${ODOO_DB_SERVER}:5432/${ODOO_DB} --username=${ODOO_DB_USERNAME} --password=${ODOO_DB_PASSWORD}"
CLASSPATH="/etc/bahmni-erp-connect.war"
CHANGE_LOG_FILE="/etc/bahmni-erp-connect/db_migration.xml"

java ${CHANGE_LOG_TABLE} -jar ${LIQUIBASE_JAR} --driver=${DRIVER} --classpath=${CLASSPATH} --changeLogFile=${CHANGE_LOG_FILE} ${CREDS} update
