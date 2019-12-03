#!/bin/bash
set -e
until PGPASSWORD=$POSTGRES_PASSWORD psql -h$DB_MART -Upostgres postgres &>/dev/null
do
  echo "Waiting for PostgreSQL..."
  sleep 1
done
if  PGPASSWORD=$POSTGRES_PASSWORD psql -h$DB_MART -Upostgres -lqt | cut -d \| -f 1 | grep -qw analytics; then
   echo "Analytics Database already exists!!"
else
    PGPASSWORD=$POSTGRES_PASSWORD psql -h$DB_MART -Upostgres <<-EOSQL
        CREATE USER analytics WITH PASSWORD '$ANALYTICS_PASSWORD';
        CREATE DATABASE analytics OWNER analytics;
EOSQL
fi
if  PGPASSWORD=$POSTGRES_PASSWORD psql -h$DB_MART -Upostgres -lqt | cut -d \| -f 1 | grep -qw metabase; then
   echo "Metabase Database already exists!!"
else
    PGPASSWORD=$POSTGRES_PASSWORD psql -h$DB_MART -Upostgres <<-EOSQL
        CREATE USER metabase WITH PASSWORD '$MB_DB_PASS';
        CREATE DATABASE metabase OWNER metabase;
EOSQL
fi