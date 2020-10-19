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
	    GRANT ALL PRIVILEGES ON DATABASE $user TO $database;
EOSQL
}

create_user_and_database clinlims clinlims clinlims

psql -U clinlims -d clinlims < /docker-entrypoint-initdb.d/db/OpenELIS_demo.sql