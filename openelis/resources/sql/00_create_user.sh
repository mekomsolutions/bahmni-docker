#!/bin/bash

RESULT_USER=`psql -Upostgres -tAc "SELECT count(*) FROM pg_roles WHERE rolname='clinlims';"`
RESULT_DB=`psql -Upostgres -tAc "SELECT count(*) from pg_catalog.pg_database where datname='clinlims';"`

if [ "$RESULT_USER" == "0" ]; then
    echo "creating postgres user - clinlims with roles CREATEDB,NOCREATEROLE,SUPERUSER,REPLICATION"
    createuser -Upostgres -d -R -s --replication clinlims;
    createuser -Upostgres -d -R -s --replication atomfeed-console;
fi

if [ "$RESULT_DB" == "0" ]; then
    createdb -Uclinlims clinlims;
    createdb -Upostgres atomfeed-console;
fi

