#!/bin/bash -e

. /usr/local/tomcat/bin/setenv.sh

DEBUG=${DEBUG:-false}
DEBUG_PORT=${DEBUG_PORT:-8000}
catalina_params=()

# wait for postgresql to initialise
wait-for-it --timeout=3600 ${ODOO_DB_SERVER}:5432

# wait for Bahmni Odoo database to be created
bahmni_database_exists () {
  echo "Waiting for '${ODOO_DB}' database to be created (host: ${ODOO_DB_SERVER})."
  PGPASSWORD=${ODOO_DB_PASSWORD} psql -h${ODOO_DB_SERVER} -U${ODOO_DB_USERNAME} -lqt | cut -d \| -f 1 | grep -qw ${ODOO_DB}
  sleep 5s
}
until bahmni_database_exists; do
  echo "Bahmni Database does not exist or 'psql' command to verify it failed."
done
echo "OK."

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
