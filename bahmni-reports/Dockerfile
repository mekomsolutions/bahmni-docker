FROM tomcat:7-jre8-alpine
ARG BAHMNI_REPORTS_URL=https://nexus.mekomsolutions.net/repository/maven-releases/org/bahmni/reports/0.92.1/reports-0.92.1.war
RUN apk add mysql-client gettext coreutils curl wget unzip bash
RUN mkdir -p /var/www/bahmni_config/ /root/.bahmni-reports/ && \
    wget -O /opt/mysql-connector-java-5.1.26.jar https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.26/mysql-connector-java-5.1.26.jar && \
    wget -O /opt/liquibase-core-2.0.5.jar   https://repo1.maven.org/maven2/org/liquibase/liquibase-core/2.0.5/liquibase-core-2.0.5.jar
RUN wget -O /tmp/bahmni-reports.war ${BAHMNI_REPORTS_URL} && \
    mv /tmp/bahmni-reports.war /usr/local/tomcat/webapps/bahmni-reports.war
RUN apk add ttf-dejavu
COPY wait-for-url.sh /usr/local/tomcat/wait-for-url.sh
COPY init-db.sh /usr/local/tomcat/init-db.sh
COPY startup.sh /usr/local/tomcat/bin/startup.sh

VOLUME /reports
RUN chmod +x /usr/local/tomcat/wait-for-url.sh /usr/local/tomcat/init-db.sh /usr/local/tomcat/bin/startup.sh

CMD ["/usr/local/tomcat/bin/startup.sh"]
