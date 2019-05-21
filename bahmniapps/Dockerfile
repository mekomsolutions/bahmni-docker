FROM httpd:2.4
RUN apt update \
&& apt install -y curl iproute2 less nano tree unzip
ARG BAHMNIAPPS_URL=https://nexus.mekomsolutions.net/repository/maven-commits/net/mekomsolutions/bahmniapps/9c3667d/bahmniapps-9c3667d.zip
RUN mkdir -p /var/www/bahmniapps/ \
 && curl --output /var/www/bahmniapps/bahmniapps-a63f511.zip ${BAHMNIAPPS_URL} \
 && unzip /var/www/bahmniapps/bahmniapps-a63f511.zip -d /var/www/bahmniapps/ \
 && rm /var/www/bahmniapps/bahmniapps-a63f511.zip
COPY resources/httpd.conf /usr/local/apache2/conf/httpd.conf
