service mysqld start
if service --status-all | grep -Fq 'postgresql-9.2'; then    
  service postgresql-9.2 start
fi
bahmni -ilocal start