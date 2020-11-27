#!/bin/sh
set -e -x

LAB_CONNECT_OMOD="/opt/liquibase/openelis-atomfeed-client.omod"
LIQUIBASE_JAR="/opt/liquibase/liquibase-core-2.0.5.jar"
OPENMRS_WAR_PATH="/opt/liquibase/openmrs.war"
ATOMFEED_CLIENT_JAR="/opt/liquibase/atomfeed-client.jar"

function run_openmrs_dependent_liquibase() {
	java -Dliquibase.databaseChangeLogTableName=liquibasechangelog -Dliquibase.databaseChangeLogLockTableName=liquibasechangeloglock -DschemaName=openmrs -jar $LIQUIBASE_JAR --driver=com.mysql.jdbc.Driver --url=jdbc:mysql://$OPENMRS_DB_SERVER:3306/openmrs --username=$OPENMRS_DB_USERNAME --password=$OPENMRS_DB_PASSWORD --classpath=$1:$OPENMRS_WAR_PATH --changeLogFile=$2 update
}

function run_atomfeed_client_liquibase() {
	run_openmrs_dependent_liquibase $ATOMFEED_CLIENT_JAR sql/db_migrations.xml

}

run_atomfeed_client_liquibase