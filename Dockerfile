FROM centos/systemd

ARG INVENTORY_FILE
ARG INSTALLER_VERSION=0.92-142

ENV LANG en_US.UTF-8
ENV PGSETUP_INITDB_OPTIONS --encoding=UTF-8

RUN yum install -y nano nmap openssh-server sudo iproute policycoreutils policycoreutils-python selinux-policy selinux-policy-targeted libselinux-utils setools setools-console
RUN yum install -y http://repo.mybahmni.org.s3.amazonaws.com/rpm/bahmni/bahmni-installer-${INSTALLER_VERSION}.noarch.rpm

COPY resources/setup.yml /etc/bahmni-installer/setup.yml
COPY inventories/${INVENTORY_FILE} /etc/bahmni-installer/local
COPY resources/install_bahmni.sh /tmp
COPY resources/start_bahmni.sh /tmp
COPY resources/odoo.conf /tmp
COPY resources/odoo /tmp

RUN chmod +x /tmp/install_bahmni.sh
RUN chmod +x /tmp/start_bahmni.sh

CMD ["/usr/sbin/init"]
