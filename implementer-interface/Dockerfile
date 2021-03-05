FROM alpine as extracter
ARG IMPLEMENTER_INTERFACE_URL=http://repo.mybahmni.org.s3.amazonaws.com/rpm/bahmni/bahmni-implementer-interface-0.93-77.noarch.rpm
RUN apk add wget zip cpio rpm2cpio \
    && wget -O /tmp/bahmni-implementer-interface.rpm ${IMPLEMENTER_INTERFACE_URL} \
    && rpm2cpio /tmp/bahmni-implementer-interface.rpm | cpio -idmv \
    && cd /opt/bahmni-implementer-interface/etc/ \
    && zip -r  /tmp/implementer_interface.zip implementer_interface/*

FROM httpd:2.4-alpine
EXPOSE 8902/tcp
RUN apk add coreutils curl wget unzip bash nano tree less iproute2

ARG TIMEZONE
RUN ln -s /usr/share/zoneinfo/$TIMEZONE /etc/localtime

COPY --from=extracter /tmp/implementer_interface.zip .
RUN mkdir -p  /var/www/ \
 && unzip -d /var/www/ implementer_interface.zip \
 && rm implementer_interface.zip
COPY resources/httpd.conf /usr/local/apache2/conf/httpd.conf
