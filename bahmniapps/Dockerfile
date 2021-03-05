FROM httpd:2.4-alpine

EXPOSE 8900/tcp

RUN apk add curl iproute2 iputils less nano tree unzip ca-certificates tzdata rsync

ARG TIMEZONE
RUN ln -s /usr/share/zoneinfo/$TIMEZONE /etc/localtime

ARG BAHMNIAPPS_URL=https://nexus.mekomsolutions.net/repository/maven-commits/net/mekomsolutions/bahmniapps/9c3667d/bahmniapps-9c3667d.zip

RUN mkdir -p /var/www/ \
 && curl --output /var/www/bahmniapps-9c3667d.zip ${BAHMNIAPPS_URL} \
 && unzip /var/www/bahmniapps-9c3667d.zip -d /var/www/ \
 && rm /var/www/bahmniapps-9c3667d.zip

COPY resources/httpd.conf /usr/local/apache2/conf/httpd.conf

COPY resources/cgi-bin/systemdate.sh /usr/local/apache2/cgi-bin/systemdate
