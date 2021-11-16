FROM tomcat:7-jre8
ARG BAHMNI_ERP_CONNECT_WAR_URL=https://nexus.mekomsolutions.net/repository/maven-releases/org/bahmni/openerp/openerp-atomfeed-service/0.94-1.0.1/openerp-atomfeed-service-0.94-1.0.1.war
RUN apt update \
&& apt install -y postgresql-client wait-for-it curl iproute2 iputils-ping less nano tree unzip ca-certificates

RUN wget -O /tmp/bahmni-erp-connect.war ${BAHMNI_ERP_CONNECT_WAR_URL} && \
    mv /tmp/bahmni-erp-connect.war /usr/local/tomcat/webapps/bahmni-erp-connect.war

RUN mkdir -p /opt/liquibase && wget -O /opt/liquibase/liquibase-core-2.0.3.jar https://repo1.maven.org/maven2/org/liquibase/liquibase-core/2.0.3/liquibase-core-2.0.3.jar

COPY startup.sh /usr/local/tomcat/bin/startup.sh
COPY setenv.sh /usr/local/tomcat/bin/setenv.sh
COPY init-db.sh /usr/local/tomcat/init-db.sh
COPY disable_product_sync.xml /opt/migrations/disable_product_sync.xml

RUN chmod +x /usr/local/tomcat/bin/startup.sh /usr/local/tomcat/init-db.sh

ENV WEBAPP_PATH ${CATALINA_HOME}/webapps
CMD ["/usr/local/tomcat/bin/startup.sh"]
