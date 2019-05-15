FROM httpd:2.4
ARG BAHMNIAPPS_URL=https://nexus.mekomsolutions.net/repository/maven-commits/net/mekomsolutions/bahmniapps/a63f511/bahmniapps-a63f511.zip
RUN apt update
RUN apt install -y nano tree less iputils-ping curl unzip
RUN mkdir -p /var/www/bahmniapps/
RUN curl --output /var/www/bahmniapps/bahmniapps-a63f511.zip ${BAHMNIAPPS_URL}
RUN unzip /var/www/bahmniapps/bahmniapps-a63f511.zip -d /var/www/bahmniapps/
RUN rm /var/www/bahmniapps/bahmniapps-a63f511.zip
COPY resources/httpd.conf /usr/local/apache2/conf/httpd.conf
