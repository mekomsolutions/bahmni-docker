export JAVA_OPTS="-DAPP_PROPERTIES_FILE=${APP_PROPERTIES_FILE} -Dfile.encoding=UTF-8 -server -Xms256m -Xmx768m -XX:PermSize=256m -XX:MaxPermSize=512m"
export CATALINA_OPTS="-DAPP_PROPERTIES_FILE=${APP_PROPERTIES_FILE}"