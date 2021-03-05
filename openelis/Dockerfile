FROM tomcat:8-jre8-alpine

ARG OPENELIS_WAR_URL=https://nexus.mekomsolutions.net/repository/maven-releases/org/bahmni/openelis/3.1/openelis-3.1.war

RUN apk add mysql-client gettext coreutils curl wget bash

RUN wget -O /tmp/openelis.war ${OPENELIS_WAR_URL} && \
    mv /tmp/openelis.war /usr/local/tomcat/webapps/openelis.war

EXPOSE 8080
ADD resources/startup.sh /startup.sh
COPY resources/setenv.sh /usr/local/tomcat/bin/setenv.sh
COPY resources/wait-for-it.sh /usr/local/tomcat/wait-for-it.sh
COPY resources/ /opt/liquibase/
CMD ["/startup.sh"]
