#!/bin/bash
set -e

declare -r TIMEOUT="$1"
declare -r HOST="$2"

wait-for-url() {
    timeout -s TERM $TIMEOUT bash -c \
    'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' ${0})" != "200" ]];\
    do echo "Waiting for ${0} to become available" && sleep 5;\
  done' ${HOST}
    echo "${HOST} returned 200."
    echo "OK."
    curl -I ${HOST}
}

wait-for-url ${HOST}
