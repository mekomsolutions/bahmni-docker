FROM httpd:2.4

MAINTAINER fabien  <fabien@mekomsolutions.com>

RUN apt update
RUN apt install -y nano tree less iputils-ping


COPY resources/httpd.conf /usr/local/apache2/conf/httpd.conf
