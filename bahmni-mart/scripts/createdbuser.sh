#!/bin/bash
set -e
until PGPASSWORD=$POSTGRES_PASSWORD psql -hpostgres-mart -Upostgres postgres &>/dev/null
do
  echo "Waiting for PostgreSQL..."
  sleep 1
done
if  PGPASSWORD=$POSTGRES_PASSWORD psql -hpostgres-mart -Upostgres -lqt | cut -d \| -f 1 | grep -qw analytics; then
   echo "Analytics Database already exists!!"
else
    PGPASSWORD=$POSTGRES_PASSWORD psql -hpostgres-mart -Upostgres <<-EOSQL
        CREATE USER analytics WITH PASSWORD '$ANALYTICS_PASSWORD';
        CREATE DATABASE analytics OWNER analytics;
EOSQL
fi