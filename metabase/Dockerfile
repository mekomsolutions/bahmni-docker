FROM tomcat:8-jre11

ARG MB_VERSION=v0.37.8
RUN apt update \
  && apt install -y postgresql-client wget

RUN wget -O /usr/local/tomcat/webapps/metabase.jar https://downloads.metabase.com/${MB_VERSION}/metabase.jar

COPY setenv.sh /usr/local/tomcat/bin/setenv.sh
COPY wait-for-it.sh /usr/local/tomcat/wait-for-it.sh
COPY startup.sh /usr/local/tomcat/startup.sh

RUN chmod +x /usr/local/tomcat/wait-for-it.sh
RUN chmod +x /usr/local/tomcat/startup.sh

CMD ["/usr/local/tomcat/startup.sh"]
