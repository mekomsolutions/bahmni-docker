#!/bin/bash


setup_properties(){
    envsubst < /tmp/application.properties > /opt/bahmni-mart/properties/application.properties
    chmod 644 /opt/bahmni-mart/properties/application.properties /opt/bahmni-mart/liquibase/liquibase.xml
}

setup_cronjob() {
   echo -e "$CRON_TIME  java -jar /opt/bahmni-mart/lib/bahmni-mart.jar --spring.config.location=\"/opt/bahmni-mart/properties/application.properties\" > /proc/1/fd/1 2>/proc/1/fd/2 \n$CRON_TIME /bin/bash /opt/flatten_odoo.sh > /proc/1/fd/1 2>/proc/1/fd/2" | crontab -
}

setup_properties
echo "[INFO] Setting up cron jobs..."
setup_cronjob
echo "[INFO] Success!"
crond -f -d 8
