FROM httpd:2.4
RUN apt update \
&& apt install -y curl iproute2 iputils-ping less nano tree unzip
RUN mkdir -p /var/www/
COPY resources/httpd.conf /usr/local/apache2/conf/httpd.conf
