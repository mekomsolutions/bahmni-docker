FROM openjdk:8-jre-alpine

# Update/Install packages
RUN apk add postgresql-client gettext tzdata bash wget && \
    mkdir -p /opt/bahmni-mart/log/ /opt/bahmni-mart/properties/ /var/www/bahmni_config/ /opt/bahmni-mart/conf/ /data/analytics /opt/bahmni-mart/lib/ && \
    ln -s /opt/bahmni-mart/bin/bahmni-mart.sh /usr/bin/bahmni-mart && \
    ln -s /opt/bahmni-mart/log /var/log/bahmni-mart

# Retrieve Bahmni Mart JAR
ARG BAHMNI_MART_URL=https://nexus.mekomsolutions.net/repository/maven-releases/org/bahmni/mart/bahmni-mart/2.0.4/bahmni-mart-2.0.4.jar
RUN wget -O /tmp/bahmni-mart.jar ${BAHMNI_MART_URL} && \
    mv /tmp/bahmni-mart.jar /opt/bahmni-mart/lib/bahmni-mart.jar

# Add configuration files
ADD scripts/ /etc/scripts/
COPY files/logback-spring.xml /opt/bahmni-mart/properties/logback-spring.xml
COPY files/application.properties /tmp/application.properties
RUN chmod 644 /opt/bahmni-mart/properties/logback-spring.xml

RUN chmod +x /etc/scripts/*

# Add Odoo flattening 'app'
COPY files/flatten_odoo.sh /opt/flatten_odoo.sh
RUN chmod +x /opt/flatten_odoo.sh

CMD ["/bin/sh", "/etc/scripts/setup.sh"]
