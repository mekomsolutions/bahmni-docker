#!/bin/bash

################################################################
#
# A bash script to move the MySQL data directory
#
#################################################################
#
# Requires to provide the 'my.cnf' file location and the new path (eg, '/mnt/data/mysql_datadir') as parameter
#
#

if [[ ! -z $1 ]] && [[ ! -z $2 ]]
  then {

    declare -A datadir
    datadir[name]="datadir"
    datadir[path]="$2"
    datadir[path_escaped]=$(echo ${datadir[path]} |sed -e 's/\//\\\//g')

    # Datadir
    if [[ $(grep  "^${datadir[name]}" $1) ]]
        then {
            echo "Update ${datadir[name]} value..."
            sed -i "s/\(^${datadir[name]}\).*/\1\=${datadir[path_escaped]}/" $1
        } else {
            echo "Set ${datadir[name]} value..."
            echo "" >> $1
            echo "# Add ${datadir[name]} - Mekom Solutions" >> $1
            echo -e "${datadir[name]}=${datadir[path]}" >> $1
        }
    fi

    declare -A socket
    socket[name]="socket"
    socket[path]="$2"
    socket[path_escaped]=$(echo ${socket[path]} |sed -e 's/\//\\\//g')

    # Socket
    if [[ $(grep  "^${socket[name]}" $1) ]]
        then {
            echo "Update ${socket[name]} value..."
            sed -i "s/\(^${socket[name]}\).*/\1\=${socket[path_escaped]}\/mysql.sock/" $1
        } else {
            echo "Set ${socket[name]} value..."
            echo "" >> $1
            echo "# Add ${socket[name]} - Mekom Solutions" >> $1
            echo -e "${socket[name]}=${socket[path]}" >> $1
        }
    fi

    # Add the client section
    echo "Add the '[client]' section and values..."
    echo "# Add the client section - Mekom Solutions" >> $1
    echo "[client]" >> $1
    echo "port=3306" >> $1
    echo "${socket[name]}=${socket[path]}/mysql.sock" >> $1

} else {
    echo "[ERROR] Parameters not provided. Please provide the 'my.cnf' file path and the new MySQL data directory path as command line parameters"
    echo "Ex: ./move_mysql_datadir.sh /etc/my.cnf /mnt/data/mysql_datadir" 
    exit 1
}
fi

exit 0
