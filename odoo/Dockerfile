FROM odoo:10.0
USER root
RUN set -x; \
        apt-get update \
        && apt-get install -y git
RUN git clone https://github.com/Bahmni/odoo-modules.git /opt/bahmni-addons
RUN cd /opt/bahmni-addons/ \
        && git checkout 37ff23e
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/
COPY wait-for-it.sh /etc/odoo/wait-for-it.sh
RUN chmod +x /etc/odoo/wait-for-it.sh
CMD ["odoo"]
