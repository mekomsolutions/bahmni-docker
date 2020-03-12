FROM tomcat:jdk8
ARG BAHMNI_REPORTS_URL=https://nexus.mekomsolutions.net/repository/maven-snapshots/org/bahmni/reports/0.92-SNAPSHOT/reports-0.92-20200310.103807-2.war
RUN apt-get update && \
    apt-get install wget mariadb-client gettext-base unzip -y && \
    mkdir -p /var/www/bahmni_config/ /root/.bahmni-reports/ && \
    wget -O /opt/mysql-connector-java-5.1.26.jar https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.26/mysql-connector-java-5.1.26.jar && \
    wget -O /opt/liquibase-core-2.0.5.jar   https://repo1.maven.org/maven2/org/liquibase/liquibase-core/2.0.5/liquibase-core-2.0.5.jar
RUN wget -O /tmp/bahmni-reports.war ${BAHMNI_REPORTS_URL} && \
    mv /tmp/bahmni-reports.war /usr/local/tomcat/webapps/bahmni-reports.war
ADD scripts/ /opt/scripts/
ADD conf/ /etc/conf/
VOLUME /reports
RUN chmod +x /opt/scripts/*

CMD ["/bin/sh", "/opt/scripts/setup.sh"]
