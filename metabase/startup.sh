#!/bin/bash -e

. /usr/local/tomcat/bin/setenv.sh

# wait for postgresql to initialise
/usr/local/tomcat/wait-for-it.sh --timeout=3600 ${MB_DB_HOST}:5432

# start tomcat
java -jar /usr/local/tomcat/webapps/metabase.jar
