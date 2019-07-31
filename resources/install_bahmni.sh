#!/bin/bash

# A bash script to install bahmni 0.92 in a docker image

bahmni -ilocal install
bahmni -ilocal stop

if systemctl | grep -q 'mysqld.service'; then    
  systemctl stop mysqld
fi


if systemctl | grep -q 'postgresql-9.6'; then    
  systemctl stop postgresql-9.6
fi

if systemctl | grep -q "odoo.service"; then
    # replace odoo.conf file
    cp -rf /tmp/odoo.conf /etc/

    # replace odoo init.d script
    cp -rf /tmp/odoo /opt/bahmni-erp/bin/
    chmod +x /opt/bahmni-erp/bin/odoo
    chown odoo:odoo /opt/bahmni-erp/bin/odoo
fi