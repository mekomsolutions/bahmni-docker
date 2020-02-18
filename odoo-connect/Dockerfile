FROM tomcat:7-jre8
RUN apt update \
&& apt install -y curl iproute2 iputils-ping less nano tree unzip ca-certificates

COPY wait-for-it.sh /usr/local/tomcat/wait-for-it.sh
COPY startup.sh /usr/local/tomcat/startup.sh
COPY setenv.sh /usr/local/tomcat/bin/setenv.sh

COPY resources/erp-atomfeed.properties /etc/bahmni-erp-connect/erp-atomfeed.properties
COPY resources/run-liquibase.sh /etc/bahmni-erp-connect/run-liquibase.sh
COPY resources/openerp-atomfeed-service.war ${CATALINA_HOME}/webapps/bahmni-erp-connect.war

RUN chmod +x /etc/bahmni-erp-connect/run-liquibase.sh
RUN chmod +x /usr/local/tomcat/wait-for-it.sh
RUN chmod +x /usr/local/tomcat/startup.sh
RUN chmod oug+x /etc/bahmni-erp-connect/run-liquibase.sh

ENV WEBAPP_PATH ${CATALINA_HOME}/webapps
CMD ["/usr/local/tomcat/startup.sh"]
