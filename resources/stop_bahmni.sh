#!/bin/sh
host_is_up()
{
	if (curl -L -k -I -s localhost/openmrs | grep -q 'HTTP/1.1 200 OK')
	then
		return 1
	else
		return 0
	fi
}
service mysqld start
if service --status-all | grep -Fq 'postgresql-9.2'; then    
  service postgresql-9.2 start
fi
bahmni -ilocal start

echo "waiting openmrs startup..."
sleep 180

bahmni -ilocal stop
service mysqld stop
if service --status-all | grep -Fq 'postgresql-9.2'; then    
  service postgresql-9.2 stop
fi