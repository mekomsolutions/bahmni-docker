FROM tomcat:8-jre11

ARG MB_VERSION=v1.36.11
RUN apt update \
  && apt install -y postgresql-client wget

RUN wget -O /usr/local/tomcat/webapps/metabase.jar https://nexus.mekomsolutions.net/repository/maven-releases/com/metabase/metabase/${MB_VERSION}/metabase-${MB_VERSION}.jar

COPY setenv.sh /usr/local/tomcat/bin/setenv.sh
COPY wait-for-it.sh /usr/local/tomcat/wait-for-it.sh
COPY startup.sh /usr/local/tomcat/startup.sh
COPY fix-wrong-refs.sql /usr/local/tomcat/fix-wrong-refs.sql

RUN chmod +x /usr/local/tomcat/wait-for-it.sh
RUN chmod +x /usr/local/tomcat/startup.sh

CMD ["/usr/local/tomcat/startup.sh"]
