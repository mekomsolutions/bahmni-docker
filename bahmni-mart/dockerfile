FROM openjdk:8-jre-alpine
ARG TIMEZONE
RUN apk add postgresql-client gettext tzdata  && \
    mkdir -p /opt/bahmni-mart/log/ /opt/bahmni-mart/properties/ /var/www/bahmni_config/ /opt/bahmni-mart/conf/ /data/analytics /opt/bahmni-mart/lib/ && \
    ln -s /opt/bahmni-mart/bin/bahmni-mart.sh /usr/bin/bahmni-mart && \
    ln -s /opt/bahmni-mart/log /var/log/bahmni-mart
ADD scripts/ /etc/scripts/
COPY files/logback-spring.xml /opt/bahmni-mart/properties/logback-spring.xml
COPY files/application.properties /tmp/application.properties
RUN chmod 644 /opt/bahmni-mart/properties/logback-spring.xml 
COPY  files/bahmni-mart-1.0.0.jar /opt/bahmni-mart/lib/bahmni-mart.jar
RUN chmod +x /etc/scripts/* && \
    cp /usr/share/zoneinfo/$TIMEZONE /etc/localtime && \
    echo "$TIMEZONE" > /etc/timezone && \
    apk del tzdata
CMD ["/bin/sh", "/etc/scripts/setup.sh"]