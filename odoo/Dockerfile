FROM python:2.7

ARG ODOO_VERSION=10.0
# ODOO_RELEASE Should be a nightly build snapshot date of ODOO_VERSION
ARG ODOO_RELEASE=20200101

RUN apt update
RUN apt -y install libsasl2-dev python-dev libldap2-dev libssl-dev \
    npm nodejs ca-certificates node-less git gettext-base wkhtmltopdf
RUN npm install -g less@3.10.3 less-plugin-clean-css

RUN addgroup odoo && adduser odoo --shel /bin/sh --disabled-password --ingroup odoo
RUN echo "odoo ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /opt && wget https://nightly.odoo.com/10.0/nightly/src/odoo_${ODOO_VERSION}.${ODOO_RELEASE}.tar.gz -q \
        && tar -xzf odoo_${ODOO_VERSION}.${ODOO_RELEASE}.tar.gz -C /opt \
        && rm odoo_${ODOO_VERSION}.${ODOO_RELEASE}.tar.gz
RUN cd /opt/odoo-${ODOO_VERSION}.post${ODOO_RELEASE} && pip install -r requirements.txt
RUN cd /opt/odoo-${ODOO_VERSION}.post${ODOO_RELEASE} && python setup.py install > /dev/null \
 && rm -r /opt/odoo-${ODOO_VERSION}.post${ODOO_RELEASE}

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY wait-for-it.sh /etc/odoo/wait-for-it.sh
RUN chmod +x /etc/odoo/wait-for-it.sh

# Mount /mnt/extra-addons for users addons
RUN mkdir -p /mnt/extra-addons \
        && chown -R odoo /mnt/extra-addons 
RUN git clone https://github.com/Bahmni/odoo-modules.git /opt/bahmni-addons
RUN cd /opt/bahmni-addons/ \
        && git checkout 37ff23e

# Expose Odoo services
EXPOSE 8069 8071

# Set the default config file
COPY odoo.conf /etc/odoo/odoo.conf
ENV ODOO_RC /etc/odoo/odoo.conf

# Set default user when running the container
ENTRYPOINT ["/entrypoint.sh"]

CMD ["odoo"]
