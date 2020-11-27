#!/bin/bash

set -eu

function create_user_and_database() {
	local database=$1
	local user=$2
	local password=$3
	echo "  Creating 'OpenELIS' user and database..."
	psql -v ON_ERROR_STOP=1 --username postgres postgres <<-EOSQL
	    CREATE USER $user WITH UNENCRYPTED PASSWORD '$password';
	    CREATE DATABASE $database;
	    GRANT ALL PRIVILEGES ON DATABASE $database TO $user;
EOSQL
}

create_user_and_database ${OPENELIS_DB_NAME} ${OPENELIS_DB_USER} ${OPENELIS_DB_PASSWORD}

psql -U ${OPENELIS_DB_USER} -d ${OPENELIS_DB_NAME} < /docker-entrypoint-initdb.d/db/OpenELIS_base.sql
