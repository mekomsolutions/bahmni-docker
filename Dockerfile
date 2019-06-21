FROM centos/systemd
ARG INVENTORY_FILE
ENV LANG en_US.UTF-8
ENV PGSETUP_INITDB_OPTIONS --encoding=UTF-8
RUN yum install -y nano
RUN yum install -y nmap
RUN yum install -y openssh-server sudo iproute policycoreutils policycoreutils-python selinux-policy selinux-policy-targeted libselinux-utils setools setools-console
RUN yum install -y http://repo.mybahmni.org.s3.amazonaws.com/rpm/bahmni/bahmni-installer-0.92-110.noarch.rpm
ADD setup.yml /etc/bahmni-installer/setup.yml
ADD inventories/${INVENTORY_FILE} /etc/bahmni-installer/local
ADD resources/install_bahmni.sh /tmp
ADD resources/start_bahmni.sh /tmp
RUN chmod +x /tmp/install_bahmni.sh
RUN chmod +x /tmp/start_bahmni.sh
CMD ["/usr/sbin/init"]