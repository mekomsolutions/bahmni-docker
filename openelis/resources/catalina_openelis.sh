#!/bin/sh
set -e -x
/bin/bash /usr/local/tomcat/bin/setenv.sh
/bin/bash catalina.sh run
