FROM tomcat:7-jre8-alpine
ARG OPENMRS_WAR_URL=https://openmrs.jfrog.io/artifactory/public/org/openmrs/web/openmrs-webapp/2.1.3/openmrs-webapp-2.1.3.war

RUN apk add mysql-client gettext coreutils curl wget

RUN wget -O /usr/local/tomcat/webapps/openmrs.war ${OPENMRS_WAR_URL}
COPY setenv.sh /usr/local/tomcat/bin/setenv.sh

COPY wait-for-it.sh /usr/local/tomcat/wait-for-it.sh
COPY startup.sh /usr/local/tomcat/startup.sh

RUN sed -i '/Connector port="8080"/a URIEncoding="UTF-8" relaxedPathChars="[]|" relaxedQueryChars="[]|{}^&#x5c;&#x60;&quot;&lt;&gt;"' /usr/local/tomcat/conf/server.xml

RUN chmod +x /usr/local/tomcat/wait-for-it.sh
RUN chmod +x /usr/local/tomcat/startup.sh

CMD ["/usr/local/tomcat/startup.sh"]
