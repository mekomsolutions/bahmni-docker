#!/bin/bash
set -e

# Extract liquibase files from WAR archive
MIGRATIONS_FILES_FOLDER="/opt/migrations"
echo "Extracting WAR archive to copy the required Liquibase and SQL files"
unzip -q -o /usr/local/tomcat/webapps/bahmni-erp-connect.war -d /tmp/bahmni-erp-connect/
mkdir -p ${MIGRATIONS_FILES_FOLDER}/
cp /tmp/bahmni-erp-connect/WEB-INF/classes/sql/db_migrations.xml ${MIGRATIONS_FILES_FOLDER}/db_migrations.xml
rm -rf /tmp/bahmni-erp-connect
echo "Done"

DISABLE_PRODUCT_SYNC=${DISABLE_PRODUCT_SYNC:-true}

ODOO_DB=${ODOO_DB:-odoo}
ODOO_DB_SERVER=${ODOO_DB_SERVER:-odoo-postgresql}
ODOO_DB_USERNAME=${ODOO_DB_USERNAME:-odoo}
ODOO_DB_PASSWORD=${ODOO_DB_PASSWORD:-password}

CHANGE_LOG_TABLE="-Dliquibase.databaseChangeLogTableName=liquibasechangelog -Dliquibase.databaseChangeLogLockTableName=liquibasechangeloglock"
LIQUIBASE_JAR="/opt/liquibase/liquibase-core-2.0.3.jar"
DRIVER="org.postgresql.Driver"
CREDS="--url=jdbc:postgresql://${ODOO_DB_SERVER}:5432/${ODOO_DB} --username=${ODOO_DB_USERNAME} --password=${ODOO_DB_PASSWORD}"
CLASSPATH="${CATALINA_HOME}/webapps/bahmni-erp-connect.war"
CHANGE_LOG_FILE="/opt/migrations/db_migrations.xml"
DISABLE_CONCEPT_SYNC_FILE="/opt/migrations/disable_product_sync.xml"

if ! java ${CHANGE_LOG_TABLE} -jar ${LIQUIBASE_JAR} --driver=${DRIVER} --classpath=${CLASSPATH} --changeLogFile=${CHANGE_LOG_FILE} ${CREDS} update; then
    echo "Clear liquibase lock"
    PGPASSWORD=$ODOO_DB_PASSWORD psql -h $ODOO_DB_SERVER -U $ODOO_DB_USERNAME $ODOO_DB -c 'UPDATE liquibasechangeloglock SET locked=FALSE;'
    java ${CHANGE_LOG_TABLE} -jar ${LIQUIBASE_JAR} --driver=${DRIVER} --classpath=${CLASSPATH} --changeLogFile=${CHANGE_LOG_FILE} ${CREDS} update
fi

if [ $DISABLE_PRODUCT_SYNC == true ]; then
    java ${CHANGE_LOG_TABLE} -jar ${LIQUIBASE_JAR} --driver=${DRIVER} --classpath=${CLASSPATH} --changeLogFile=${DISABLE_CONCEPT_SYNC_FILE} ${CREDS} update
fi
