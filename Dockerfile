FROM centos:6.9
ARG INVENTORY_FILE
RUN yum update -y && yum upgrade -y
RUN yum install -y ftp://195.220.108.108/linux/Mandriva/devel/cooker/x86_64/media/contrib/release/mx-1.4.5-1-mdv2012.0.x86_64.rpm
RUN yum install -y python-setuptools sudo policycoreutils policycoreutils-python selinux-policy selinux-policy-targeted libselinux-utils setools openssh-server openssh-clients
RUN yum install -y https://dl.bintray.com/bahmni/rpm/rpms/bahmni-installer-0.90-308.noarch.rpm
ADD setup.yml /etc/bahmni-installer/setup.yml
ADD inventories/${INVENTORY_FILE} /etc/bahmni-installer/local
ADD resources/stop_bahmni.sh /tmp
ADD resources/start_bahmni.sh /tmp
RUN chmod +x /tmp/stop_bahmni.sh /tmp/start_bahmni.sh
RUN bahmni -ilocal install && /tmp/stop_bahmni.sh && rm /tmp/stop_bahmni.sh 
ENTRYPOINT /tmp/start_bahmni.sh ; /bin/bash