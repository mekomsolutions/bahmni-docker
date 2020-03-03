#!/bin/bash

set -e

# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the odoo process if not present in the config file
: ${HOST:=${DB_PORT_5432_TCP_ADDR:='db'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=5432}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='odoo'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}

: ${ODOO_ADDONS_PATH='/mnt/extra-addons/.'}
: ${ADDONS_LIST:=${DEFAULT_ADDONS_LIST:='base,stock,sale,point_of_sale,purchase,bahmni_account,bahmni_atom_feed,bahmni_product,bahmni_purchase,bahmni_sale,bahmni_stock,bahmni_web_extension'}}

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
  odoo_addons=" -u $ADDONS_LIST"
  for addon in $addons
  do
    if [[ $addon != .* ]]
    then
      odoo_addons+=",$addon"
    fi
  done

  odoo_addons+=" -i $ADDONS_LIST"

  for addon in $addons
  do
    if [[ $addon != .* ]]
    then
      odoo_addons+=",$addon"
    fi
  done
}

odoo_addons_param

/etc/odoo/wait-for-it.sh --timeout=3600 ${HOST}:${PORT}

sleep 5

echo "Installing base Odoo & Bahmni Addons"

exec `odoo $odoo_addons --stop-after-init --without-demo=all -d bahmni ${DB_ARGS[@]}`

echo "Addons installed successfully, Restarting Odoo and initializating"

case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec odoo "$@"
        else
            exec `odoo --without-demo=all -d bahmni ${DB_ARGS[@]}`
        fi
        ;;
    -*)
        exec odoo "--without-demo=all -d bahmni $@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1