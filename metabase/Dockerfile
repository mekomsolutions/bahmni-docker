FROM tomcat:8-jdk11-adoptopenjdk-hotspot

ARG MB_VERSION=v1.36.11
RUN mkdir -p /usr/share/man/man1 && mkdir -p /usr/share/man/man7
RUN apt update \
  && apt install -y postgresql-client wget jq curl

RUN wget -O /usr/local/tomcat/webapps/metabase.jar https://nexus.mekomsolutions.net/repository/maven-releases/com/metabase/metabase/${MB_VERSION}/metabase-${MB_VERSION}.jar

COPY setenv.sh /usr/local/tomcat/bin/setenv.sh
COPY wait-for-it.sh /usr/local/tomcat/wait-for-it.sh
COPY startup.sh /usr/local/tomcat/startup.sh
COPY fix-wrong-refs.sql /usr/local/tomcat/fix-wrong-refs.sql
COPY create_users.sh /usr/local/tomcat/create_users.sh

RUN chmod +x /usr/local/tomcat/wait-for-it.sh
RUN chmod +x /usr/local/tomcat/startup.sh
RUN chmod +x /usr/local/tomcat/create_users.sh

CMD ["/usr/local/tomcat/startup.sh"]
