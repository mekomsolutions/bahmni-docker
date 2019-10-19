#!/bin/bash

manage_user_and_group() {
    addgroup -S bahmni
    adduser -S bahmni -G bahmni
}

create_mart_directories() {
    if [ ! -d /opt/bahmni-mart/log/ ]; then
        mkdir -p /opt/bahmni-mart/log/
    fi

    if [ ! -d /opt/bahmni-mart/properties/ ]; then
        mkdir -p /opt/bahmni-mart/properties/
    fi

    if [ ! -d /var/www/bahmni_config/ ]; then
        mkdir -p /var/www/bahmni_config/
    fi

    if [ ! -d /opt/bahmni-mart/conf/ ]; then
        mkdir -p /opt/bahmni-mart/conf/
    fi

    if [ ! -d /data/analytics ]; then
        mkdir -p /data/analytics
    fi

    if [ ! -d /opt/bahmni-mart/lib/ ]; then
        mkdir -p /opt/bahmni-mart/lib/
    fi

}

link_directories() {
    #create links
    ln -s /opt/bahmni-mart/bin/bahmni-mart.sh /usr/bin/bahmni-mart
    ln -s /opt/bahmni-mart/log /var/log/bahmni-mart

    if [ ! -d /var/www/bahmni_config/bahmni-mart/ ]; then
        ln -s /opt/bahmni-mart/conf /var/www/bahmni_config/bahmni-mart
    fi
}

manage_permissions() {
    # permissions
    chown -R bahmni:bahmni /usr/bin/bahmni-mart
    chown -R bahmni:bahmni /opt/bahmni-mart
    chown -R bahmni:bahmni /var/log/bahmni-mart
}

move_files(){
    mv /etc/files/logback-spring.xml /opt/bahmni-mart/properties/logback-spring.xml
    mv /etc/files/liquibase.xml /opt/bahmni-mart/conf/liquibase.xml
    envsubst < /etc/files/application.properties > /opt/bahmni-mart/properties/application.properties
    mv /etc/files/bahmni-mart-1.0.0.jar /opt/bahmni-mart/lib/bahmni-mart.jar
    chown bahmni:bahmni /opt/bahmni-mart/properties/logback-spring.xml  /opt/bahmni-mart/conf/liquibase.xml /opt/bahmni-mart/properties/application.properties
    chmod 644 /opt/bahmni-mart/properties/logback-spring.xml /opt/bahmni-mart/properties/application.properties
    chmod 766 /opt/bahmni-mart/conf/liquibase.xml
}

setup_cronjob() {
    # adding cron job for scheduling the job at 11:30PM everyday
   echo "$CRON_TIME  java -jar /opt/bahmni-mart/lib/bahmni-mart.jar --spring.config.location=\"/opt/bahmni-mart/properties/application.properties\" >> /var/log/bahmni-mart/bahmni-mart.log" | crontab - 
}

manage_user_and_group
create_mart_directories
link_directories
manage_permissions
move_files
echo "*********** PSQL DB Creation Starts   ******************"
sh /etc/scripts/createdbuser.sh
echo "*********** PSQL DB Creation Ends   ******************"
setup_cronjob
echo "********** Post Install Script Completed ***************"
crond -f