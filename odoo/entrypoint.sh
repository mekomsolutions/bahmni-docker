#!/bin/bash

set -e

# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the odoo process if not present in the config file
: ${HOST:=${DB_PORT_5432_TCP_ADDR:='db'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=5432}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='odoo'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}

: ${ODOO_ADDONS_PATH='/mnt/extra-addons/.'}

DB_ARGS=()
function check_config() {
    param="$1"
    value="$2"
    if ! grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then
        DB_ARGS+=("--${param}")
        DB_ARGS+=("${value}")
   fi;
}
check_config "db_host" "$HOST"
check_config "db_port" "$PORT"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"

function odoo_addons_param() {
  addons=$(find $ODOO_ADDONS_PATH -maxdepth 1 -type d -printf '%f\n')
  odoo_addons=" -u base"
  for addon in $addons
  do
    if [[ $addon != .* ]]
    then
      odoo_addons+=",$addon"
    fi
  done

  odoo_addons+=" -i stock,sale,point_of_sale,mail,purchase,"

  for addon in $addons
  do
    if [[ $addon != .* ]]
    then
      odoo_addons+="$addon,"
    fi
  done
  odoo_addons=${odoo_addons%?}
  odoo_addons+=" "
}

odoo_addons_param
sleep 5


case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec odoo "$@"
        else
            echo "I'm here"
            exec `odoo $odoo_addons --without-demo=all -d bahmni ${DB_ARGS[@]}`
        fi
        ;;
    -*)
        echo "I'm somewhere else"
        echo "$@"
        exec odoo "$odoo_addons --without-demo=all -d bahmni $@" "${DB_ARGS[@]}"
        ;;
    *)
        echo "No Way!"
        exec "$@"
esac

exit 1