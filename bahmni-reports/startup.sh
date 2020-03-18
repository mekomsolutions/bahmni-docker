#!/bin/bash
set -e
sh /usr/local/tomcat/init-db.sh
envsubst < /etc/conf/bahmni-reports.properties > /root/.bahmni-reports/bahmni-reports.properties

DEBUG=${DEBUG:-false}
DEBUG_PORT=${DEBUG_PORT:-8000}
catalina_params=()

if [ $DEBUG == true ]; then
    export JPDA_ADDRESS=$DEBUG_PORT
    export JPDA_TRANSPORT=dt_socket
    catalina_params+=(jpda)
fi
catalina_params+=(run)

# start tomcat
/usr/local/tomcat/bin/catalina.sh "${catalina_params[@]}"
