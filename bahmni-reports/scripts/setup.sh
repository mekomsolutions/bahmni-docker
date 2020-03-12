#!/bin/bash
set -e
sh /opt/scripts/init-db.sh
envsubst < /etc/conf/bahmni-reports.properties > /root/.bahmni-reports/bahmni-reports.properties
sh /usr/local/tomcat/bin/catalina.sh run
