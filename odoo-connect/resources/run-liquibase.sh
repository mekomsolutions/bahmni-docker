#!/bin/sh
set -e -x

ODOO_DB=${ODOO_DB:-bahmni}
ODOO_DB_SERVER=${ODOO_DB_SERVER:-odoo-postgresql}
ODOO_DB_USERNAME=${ODOO_DB_USERNAME:-odoo}
ODOO_DB_PASSWORD=${ODOO_DB_PASSWORD:-odoo}

CHANGE_LOG_TABLE="-Dliquibase.databaseChangeLogTableName=liquibasechangelog -Dliquibase.databaseChangeLogLockTableName=liquibasechangeloglock"
LIQUIBASE_JAR="/etc/bahmni-erp-connect/liquibase-core-2.0.3.jar"
DRIVER="org.postgresql.Driver"
CREDS="--url=jdbc:postgresql://${ODOO_DB_SERVER}:5432/${ODOO_DB} --username=${ODOO_DB_USERNAME} --password=${ODOO_DB_PASSWORD}"
CLASSPATH="${CATALINA_HOME}/webapps/bahmni-erp-connect.war"
CHANGE_LOG_FILE="/etc/bahmni-erp-connect/db_migration.xml"

java ${CHANGE_LOG_TABLE} -jar ${LIQUIBASE_JAR} --driver=${DRIVER} --classpath=${CLASSPATH} --changeLogFile=${CHANGE_LOG_FILE} ${CREDS} update
