#!/bin/bash

echo "[INFO]"
echo "[INFO] Running $0..."
echo "[INFO]"
odoo_queries_path=/var/www/bahmni_config/bahmni-mart/odoo_queries

ODOO_DB_HOST=${ERP_DB_HOSTNAME}
ODOO_DB_PORT=5432
ODOO_DB_NAME=${ERP_DB_NAME}
ODOO_DB_USER=${ERP_DB_USERNAME}
ODOO_DB_PASSWORD=${ERP_DB_PASSWORD}

ANALYTICS_DB_HOST=${ANALYTICS_DB_HOST}
ANALYTICS_DB_PORT=5432
ANALYTICS_DB_NAME=${ANALYTICS_DB_NAME}
ANALYTICS_DB_USER=${ANALYTICS_DB_USER}
ANALYTICS_DB_PASSWORD=${ANALYTICS_DB_PASSWORD}

flatten() {
  # Set .pgpass to store passwords
  echo "[INFO] Set credentials"
  echo -e "${ODOO_DB_HOST}:${ODOO_DB_PORT}:${ODOO_DB_NAME}:${ODOO_DB_USER}:${ODOO_DB_PASSWORD}\n${ANALYTICS_DB_HOST}:${ANALYTICS_DB_PORT}:${ANALYTICS_DB_NAME}:analytics:password" > /root/.pgpass
  chmod 0600 /root/.pgpass

  # Create the flattened temporary table
  echo "[INFO] Create 'temporary_table' from $table.sql query"
  psql -h ${ODOO_DB_HOST} -U ${ODOO_DB_USER} -d ${ODOO_DB_NAME} -c "DROP TABLE IF EXISTS temporary_table;"
  psql -h ${ODOO_DB_HOST} -U ${ODOO_DB_USER} -d ${ODOO_DB_NAME} -f ${odoo_queries_path}/$1.sql

  # Extract it
  echo "[INFO] Save 'temporary_table' to '$1.dump'"
  pg_dump -h ${ODOO_DB_HOST} -U ${ODOO_DB_USER} -d ${ODOO_DB_NAME} --table temporary_table > $1.dump
  sed -i "s/${ODOO_DB_USER}/${ANALYTICS_DB_USER}/" $1.dump
  sed -i "s/temporary_table/${table}/" $1.dump

  # Remove it
  echo "[INFO] Remove 'temporary_table'"
  psql -h ${ODOO_DB_HOST} -U ${ODOO_DB_USER} -d ${ODOO_DB_NAME} -c "DROP TABLE IF EXISTS temporary_table;"

  # Restore the table on 'analytics' DB
  echo "[INFO] Load '$1.dump' on '${ANALYTICS_DB_NAME}' database as '$1' table."
  psql -h ${ANALYTICS_DB_HOST} -U ${ANALYTICS_DB_USER} -d ${ANALYTICS_DB_NAME} -c "DROP TABLE IF EXISTS $1;"
  psql -h ${ANALYTICS_DB_HOST} -U ${ANALYTICS_DB_USER} -d ${ANALYTICS_DB_NAME} < $1.dump

  echo "[INFO] Successfully loaded '${filename%.sql}' table."
  echo "[INFO]"
}

# Scan the odoo_queries_path and process each file found
if [ -z "$(ls ${odoo_queries_path})" ]
then
  echo "[ERROR] '${odoo_queries_path}/' is empty or non-existing. Abort."
  echo "[INFO]"
  exit 1
else
  for filename in $(ls ${odoo_queries_path})
  do
    echo "[INFO] Processing '${filename%.sql}'"
    table=${filename%.sql}
  	flatten $table
  done
fi

exit
