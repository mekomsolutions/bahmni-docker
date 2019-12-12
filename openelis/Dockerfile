FROM tomcat:8-jdk8
ADD resources/openelis.war /usr/local/tomcat/webapps/
EXPOSE 8080
ADD resources/catalina_openelis.sh /catalina-openelis.sh
COPY resources/setenv.sh /usr/local/tomcat/bin/setenv.sh
CMD ["/catalina-openelis.sh"]