FROM tomcat:8-jdk8

ARG BAHMNI_ERP_CONNECT_WAR_URL=https://nexus.mekomsolutions.net/repository/maven-releases/org/bahmni/openelis/3.1/openelis-3.1.war

RUN apt update \
  && apt install -y gettext-base

RUN wget -O /tmp/openelis.war ${BAHMNI_ERP_CONNECT_WAR_URL} && \
    mv /tmp/openelis.war /usr/local/tomcat/webapps/openelis.war

EXPOSE 8080
ADD resources/startup.sh /startup.sh
COPY resources/setenv.sh /usr/local/tomcat/bin/setenv.sh
CMD ["/startup.sh"]
