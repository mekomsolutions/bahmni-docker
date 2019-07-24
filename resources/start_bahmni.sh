#!/bin/bash

if service --status-all | grep -Fq 'mysqld'; then    
  service mysqld start
fi

if service --status-all | grep -Fq 'postgresql-9.6'; then    
  service postgresql-9.6 start
fi

bahmni -ilocal start