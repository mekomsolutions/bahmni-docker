FROM httpd:2.4
EXPOSE 8901/tcp
RUN apt update \
&& apt install -y curl iproute2 iputils-ping less nano tree unzip ca-certificates
RUN mkdir -p /var/www/
COPY resources/httpd.conf /usr/local/apache2/conf/httpd.conf
