#!/bin/bash

if systemctl | grep -q 'mysqld.service'; then    
  systemctl start mysqld
fi

if systemctl | grep -q 'postgresql-9.6'; then    
  systemctl start postgresql-9.6
fi

bahmni -ilocal start