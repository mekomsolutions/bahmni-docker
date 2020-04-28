FROM httpd:2.4
RUN apt update \
  && apt install -y curl iproute2 iputils-ping less nano tree ca-certificates
COPY resources/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY resources/proxy-rules /usr/local/apache2/conf/proxy-rules
COPY resources/tls/cert.pem resources/tls/privkey.pem /etc/tls/
