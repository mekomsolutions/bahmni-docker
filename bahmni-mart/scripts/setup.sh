#!/bin/bash


setup_properties(){
    envsubst < /tmp/application.properties > /opt/bahmni-mart/properties/application.properties
    chmod 644 /opt/bahmni-mart/properties/application.properties /opt/bahmni-mart/conf/liquibase.xml
}

setup_cronjob() {
    # adding cron job for scheduling the job at 11:30PM everyday
   echo "$CRON_TIME  java -jar /opt/bahmni-mart/lib/bahmni-mart.jar --spring.config.location=\"/opt/bahmni-mart/properties/application.properties\" > /proc/1/fd/1 2>/proc/1/fd/2" | crontab - 
}

check_config
setup_properties
echo "*********** PSQL DB Creation Starts   ******************"
sh /etc/scripts/createdbuser.sh
echo "*********** PSQL DB Creation Ends   ******************"
setup_cronjob
echo "********** Post Install Script Completed ***************"
crond -f -d 8