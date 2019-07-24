#!/bin/bash

# A bash script to install bahmni 0.92 in a docker image

bahmni -ilocal install 
bahmni -ilocal stop

if service --status-all | grep -Fq 'mysqld'; then    
  service mysqld stop 
fi

if service --status-all | grep -Fq 'postgresql-9.6'; then    
  service postgresql-9.6 stop
fi

if systemctl | grep "odoo"; then
    # replace odoo.conf file
    cp -rf /tmp/odoo.conf /etc/

    # replace odoo init.d script
    cp -rf /tmp/odoo /opt/bahmni-erp/bin/
    chmod +x /opt/bahmni-erp/bin/odoo
    chown odoo:odoo /opt/bahmni-erp/bin/odoo
fi