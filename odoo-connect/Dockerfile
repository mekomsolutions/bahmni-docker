FROM tomcat:7-jre8
RUN apt update \
&& apt install -y curl iproute2 iputils-ping less nano tree unzip ca-certificates

COPY wait-for-it.sh /usr/local/tomcat/wait-for-it.sh
COPY startup.sh /usr/local/tomcat/startup.sh
COPY setenv.sh /usr/local/tomcat/bin/setenv.sh

RUN wget -O /etc/liquibase-core-2.0.3.jar https://repo1.maven.org/maven2/org/liquibase/liquibase-core/2.0.3/liquibase-core-2.0.3.jar
COPY resources/erp-atomfeed.properties /etc/bahmni-erp-connect/erp-atomfeed.properties
COPY resources/run-liquibase.sh /etc/bahmni-erp-connect/run-liquibase.sh
COPY resources/db_migration.xml /etc/bahmni-erp-connect/db_migration.xml
COPY resources/openerp-atomfeed-service.war ${CATALINA_HOME}/webapps/bahmni-erp-connect.war
COPY resources/openerp-atomfeed-service.war /etc/bahmni-erp-connect.war
COPY resources/bahmni-erp-connect.jar /etc/bahmni-erp-connect.jar

COPY start.sh /etc/bahmni-erp-connect/start.sh


RUN chmod +x /etc/bahmni-erp-connect/run-liquibase.sh
RUN chmod +x /usr/local/tomcat/wait-for-it.sh
RUN chmod +x /usr/local/tomcat/startup.sh
RUN chmod oug+x /etc/bahmni-erp-connect/run-liquibase.sh

ENV WEBAPP_PATH ${CATALINA_HOME}/webapps
CMD ["/usr/local/tomcat/startup.sh"]
