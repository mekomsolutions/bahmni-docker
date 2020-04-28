#!/bin/bash
set -e

# Extract liquibase files from WAR archive
MIGRATIONS_FILES_FOLDER="/opt/migrations"
echo "Extracting WAR archive to copy the required Liquibase and SQL files"
unzip -q -o /usr/local/tomcat/webapps/bahmni-reports.war -d /tmp/bahmni-reports/
mkdir -p ${MIGRATIONS_FILES_FOLDER}/sql/quartz
cp /tmp/bahmni-reports/WEB-INF/classes/liquibase.xml ${MIGRATIONS_FILES_FOLDER}/liquibase-openmrs.xml
cp /tmp/bahmni-reports/WEB-INF/classes/liquibase_bahmni_reports.xml ${MIGRATIONS_FILES_FOLDER}/liquibase-bahmni-reports.xml
cp /tmp/bahmni-reports/WEB-INF/classes/sql/quartz/tables_mysql_innodb.sql ${MIGRATIONS_FILES_FOLDER}/sql/quartz/tables_mysql_innodb.sql
rm -rf /tmp/bahmni-reports
echo "Done"

run_migrations(){

  echo "Running liquibase migrations"
  CHANGE_LOG_TABLE="-Dliquibase.databaseChangeLogTableName=liquibasechangelog -Dliquibase.databaseChangeLogLockTableName=liquibasechangeloglock -DschemaName=$3"
  LIQUIBASE_JAR="/opt/liquibase-core-2.0.5.jar"
  DRIVER="com.mysql.jdbc.Driver"
  CLASSPATH="/opt/mysql-connector-java-5.1.26.jar"
  CHANGE_LOG_FILE="$1"

  (cd ${MIGRATIONS_FILES_FOLDER}/ && java $CHANGE_LOG_TABLE  -jar $LIQUIBASE_JAR --driver=$DRIVER --classpath=$CLASSPATH --changeLogFile=$CHANGE_LOG_FILE --url=jdbc:mysql://$2:3306/$3 --username=$4 --password=$5 update)
}

/usr/local/tomcat/wait-for-url.sh 3600 http://${OPENMRS_HOSTNAME}:8080/openmrs/index.htm

RESULT=$(mysql -h $REPORTS_DB_HOSTNAME -u$MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD --skip-column-names -e "SHOW DATABASES LIKE 'bahmni_reports'")
if [ "$RESULT" != "bahmni_reports" ] ; then
  echo "*********** DB Creation & Migrations  ******************"
  echo "OpenMRS:"
  run_migrations liquibase-openmrs.xml $OPENMRS_DB_HOSTNAME $OPENMRS_DB_NAME $MYSQL_ROOT_USER ${MYSQL_ROOT_PASSWORD}
  echo "Bahmni Reports:"
  mysql -h $REPORTS_DB_HOSTNAME -u$MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE bahmni_reports;"
  mysql -h $REPORTS_DB_HOSTNAME -u$MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON bahmni_reports.* TO '$REPORTS_DB_USERNAME'@'%' identified by '$REPORTS_DB_PASSWORD' WITH GRANT OPTION; FLUSH PRIVILEGES;"
  run_migrations liquibase-bahmni-reports.xml $REPORTS_DB_HOSTNAME bahmni_reports $REPORTS_DB_USERNAME $REPORTS_DB_PASSWORD
fi
