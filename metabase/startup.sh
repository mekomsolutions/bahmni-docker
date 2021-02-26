#!/bin/bash -e

. /usr/local/tomcat/bin/setenv.sh

# Wait for postgresql to initialise
/usr/local/tomcat/wait-for-it.sh --timeout=3600 ${MB_DB_HOST}:5432

cat > ~/.pgpass << EOF
${MB_DB_HOST}:${MB_DB_PORT:-5432}:${MB_DB_DBNAME}:${MB_DB_USER}:${MB_DB_PASS}
EOF
chmod 600 ~/.pgpass

# Start tomcat in the background
java -jar /usr/local/tomcat/webapps/metabase.jar &

# Create Basic users
/usr/local/tomcat/create_users.sh

# Load the config
java -jar /usr/local/tomcat/webapps/metabase.jar load /opt/metabase-config --mode update

# Fix the wrong refs
wrong_ref_updates=1

while [ "$wrong_ref_updates" -gt 0 ]
do
    result=$(psql -h ${MB_DB_HOST} -U ${MB_DB_USER} -d ${MB_DB_DBNAME} -a -f /usr/local/tomcat/fix-wrong-refs.sql | tail -n 1)    
    results=($result)
    wrong_ref_updates=${results[1]}
done

# Bring tomcat to the foreground
wait ${!}