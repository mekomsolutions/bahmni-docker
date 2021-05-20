#!/bin/bash -e

DB_CREATE_TABLES=${DB_CREATE_TABLES:-false}
DB_AUTO_UPDATE=${DB_AUTO_UPDATE:-false}
MODULE_WEB_ADMIN=${MODULE_WEB_ADMIN:-true}
DEBUG=${DEBUG:-false}
DEBUG_PORT=${DEBUG_PORT:-8000}
openmrs_runtime_props_path="/usr/local/tomcat/.OpenMRS/openmrs-runtime.properties"
catalina_params=()

echo "📑 Set 'openmrs-server.properties'"
cat > /usr/local/tomcat/openmrs-server.properties << EOF
install_method=auto
connection.url=jdbc\:mysql\://${DB_HOST}\:3306/${DB_DATABASE}?autoReconnect\=true&sessionVariables\=default_storage_engine\=InnoDB&useUnicode\=true&characterEncoding\=UTF-8
connection.username=${DB_USERNAME}
connection.password=${DB_PASSWORD}
has_current_openmrs_database=true
create_database_user=false
module_web_admin=${MODULE_WEB_ADMIN}
create_tables=${DB_CREATE_TABLES}
auto_update_database=${DB_AUTO_UPDATE}
EOF

# Substitute environment variables in all properties files
echo "📑 Substitute environment variables found in /etc/properties/"
mkdir -p /tmp/properties/
propertiesFiles=`ls -p /etc/properties/ | grep -v /`
for file in $propertiesFiles
do
    envsubst < /etc/properties/${file} > /tmp/properties/${file}
    # Copy only properties that are not *-runtime.properties to application directory.
    # Leave *-runtime.properties here for further processing.
    if [[ ${file} != *"-runtime.properties" ]]; then
      echo "Moving ${file} to '/usr/local/tomcat/.OpenMRS/'"
      mv /tmp/properties/${file} /usr/local/tomcat/.OpenMRS/
    fi
done

# wait for mysql to initialise
echo "⏱  Wait for the database to start (${DB_HOST}:3306)..."
/usr/local/tomcat/wait-for-it.sh --timeout=3600 ${DB_HOST}:3306

echo "🔑 Set database credentials for further queries"
# create datbase credentials file to check the existance of data
mkdir -p /etc/mysql/ && touch /etc/mysql/db-credentials.cnf
cat > /etc/mysql/db-credentials.cnf << EOF
[client]
user=${DB_USERNAME}
password=${DB_PASSWORD}
EOF

if [ ! -e ${openmrs_runtime_props_path} ]; then
    echo "ℹ️  ${openmrs_runtime_props_path} file is missing."

    encryption_key=`openssl rand -base64 22 | sed 's/=/\\\=/g'`
    encryption_vector=`openssl rand -base64 22 | sed 's/=/\\\=/g'`

    echo "Creating it."
    cat > ${openmrs_runtime_props_path} << EOF
encryption.vector=${encryption_vector}
encryption.key=${encryption_key}
connection.url=jdbc\:mysql\://${DB_HOST}\:3306/${DB_DATABASE}?autoReconnect\=true&sessionVariables\=default_storage_engine\=InnoDB&useUnicode\=true&characterEncoding\=UTF-8
module.allow_web_admin=true
auto_update_database==${DB_AUTO_UPDATE}
connection.username=${DB_USERNAME}
connection.driver_class=com.mysql.jdbc.Driver
connection.password=${DB_PASSWORD}
EOF
fi

# Merge additional runtime props
echo "🔨 Merge additional *-runtime.properties files"
extraRuntimePropertiesFile=`find /tmp/properties/*-runtime.properties -maxdepth 1 -type f -print0 | xargs -0r ls`
for file in $extraRuntimePropertiesFile
do
    cp $openmrs_runtime_props_path /tmp/openmrs-runtime.properties
    cat ${file} /tmp/openmrs-runtime.properties |
    tac |
    awk -F'=' '!seen[$1]++' |
    tac > $openmrs_runtime_props_path
    rm ${file}
done

echo "📑 Create OpenMRS database"
mysql --defaults-extra-file=/etc/mysql/db-credentials.cnf -h${DB_HOST} -e "CREATE DATABASE IF NOT EXISTS ${DB_DATABASE}"

echo "🔬 Inspect 'opemnrs-runtime.properties':"
cat  $openmrs_runtime_props_path

echo "🔧 Set debug mode to \$DEBUG ==  $DEBUG"
if [ $DEBUG == true ]; then
    export JPDA_ADDRESS=$DEBUG_PORT
    export JPDA_TRANSPORT=dt_socket
    catalina_params+=(jpda)
fi
catalina_params+=(run)

# start tomcat
echo "🩺 Start OpenMRS"
/usr/local/tomcat/bin/catalina.sh "${catalina_params[@]}" &

# trigger first filter to start database initialization
sleep 15
curl -L http://localhost:8080/openmrs/ > /dev/null
sleep 15

# bring tomcat process to foreground again
wait ${!}
