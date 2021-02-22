#!/bin/bash -e

. /usr/local/tomcat/bin/setenv.sh

# wait for postgresql to initialise
/usr/local/tomcat/wait-for-it.sh --timeout=3600 ${MB_DB_HOST}:5432

cat > ~/.pgpass << EOF
${MB_DB_HOST}:${MB_DB_PORT:-5432}:${MB_DB_DBNAME}:${MB_DB_USER}:${MB_DB_PASS}
EOF
chmod 600 ~/.pgpass

java -jar /usr/local/tomcat/webapps/metabase.jar load /opt/metabase-config --mode update

psql -h ${MB_DB_HOST} -U ${MB_DB_USER} -d ${MB_DB_DBNAME} -a -f /usr/local/tomcat/fix-wrong-refs.sql

# start tomcat
java -jar /usr/local/tomcat/webapps/metabase.jar
