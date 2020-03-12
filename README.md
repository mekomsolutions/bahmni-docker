# Bahmni Docker

Docker Compose project to start a Bahmni server locally.

<p align="left">
  <img src="./readme/bahmni-logo-square.png" alt="Bahmni Logo" height="155">
  <img src="./readme/plus.png" alt="plus sign" height="50">
  <img src="./readme/vertical-logo-monochromatic.png" alt="Docker Logo" height="150">
  </p>

## Quick Start

### Clone the project:
```
git clone https://github.com/mekomsolutions/bahmni-docker
cd bahmni-docker
```

### Retrieve the Bahmni distribution of your choice:

The Docker images do not provide a default Bahmni distribution yet, therefore you need to first fetch one.

You can use the Haiti distribution for example:
- fetch the Maven artifact
```
mvn dependency:get -DrepoUrl=https://nexus.mekomsolutions.net/repository/maven-public -Dartifact=net.mekomsolutions:bahmni-distro-haiti:1.0.0-SNAPSHOT:zip
```
- copy it in `/tmp/bahmni-distro-haiti/`
```
mvn dependency:copy -Dartifact=net.mekomsolutions:bahmni-distro-haiti:1.0.0-SNAPSHOT:zip -DoutputDirectory=/tmp/bahmni-distro-haiti/
```
- unzip it in `/tmp/bahmni-distro-haiti/`
```
unzip /tmp/bahmni-distro-haiti/bahmni-distro-haiti-1.0.0-20200130.172847-69.zip -d /tmp/bahmni-distro-haiti/
```

### Export the variables:

Export all variables at once:
```
GROUP=haiti; DISTRO_PATH=/tmp/bahmni-distro-$GROUP; export OPENMRS_CONFIG_PATH=$DISTRO_PATH/openmrs_config; export BAHMNI_CONFIG_PATH=$DISTRO_PATH/bahmni_config; export OPENMRS_MODULES_PATH=$DISTRO_PATH/openmrs_modules; export BAHMNI_APPS_PATH=$DISTRO_PATH/bahmni_emr/bahmniapps
```

### Start Bahmni:
```
docker-compose up
```
<p align="center">
<img src="./readme/docker-compose-up-shadow.png" alt="docker-compose up" height="200">
</p>

This assumes that you run the `docker` command as the same user and in the same window in which you exported your variables.
If Docker is run as `sudo`, the variables won't have an effect. Make sure to either export them as root, or run `docker` with `sudo -E` option to preserve the user environment.

### Access the servers:

- Bahmni: http://localhost/

<p align="left">
<img src="./readme/bahmni-EMR-login-shadow.png" alt="Bahmni EMR login screen" width="300">
</p>


- OpenMRS: http://localhost/openmrs

<p align="left">
<img src="./readme/openmrs-login-shadow.png" alt="OpenMRS login screen" width="300">
</p>

- Odoo: http://localhost:8069/

<p align="left">
<img src="./readme/odoo-login.png" alt="Odoo login screen" width="300">
</p>

- Metabase: http://localhost:9003/

<p align="left">
<img src="./readme/metabase-login-shadow.png" alt="Metabase login screen" width="300">
</p>

## Advanced

### TLS support

To enable TLS support, just add the line:

```
  command: "httpd-foreground -DenableTLS"
```
to the `proxy` service in the [docker-compose.yml](./docker-compose.yml) file.

Default certificates are self-signed and therefore unsecured.

Provide your own valid certificates as a bound volume mounted at `/etc/tls/`.

The `proxy` service would look like:
```
services:
  proxy:
    command: "httpd-foreground -DenableTLS"
    build:
      [...]
    volumes:
    - "/etc/letsencrypt/live/domain.com/:/etc/tls/"
    - [...]

```
### Start with a custom MySQL dump

To start OpenMRS with your own database, just drop your data file (`.sql` or `.sql.gz`) in the [./sqls/mysql/](./sqls/mysql/) folder and recreate your volumes (`docker-compose -v down`).


### Disable individual services
If you are developing, you may not want to run the complete Bahmni suite.
You can disable services by adding **docker-compose.override.yml** file at the project root with the following contents:

**./docker-compose.override.yml**
```
#
# Example file to disable docker-compose.yml services.
#
version: "3.7"

services:
  metabase:
    entrypoint: ["echo", "[ERROR] Service is disabled in docker-compose.override.yml file"]
  bahmni-mart:
    entrypoint: ["echo", "[ERROR] Service is disabled in docker-compose.override.yml file"]
  db-mart:
    entrypoint: ["echo", "[ERROR] Service is disabled in docker-compose.override.yml file"]
```

You can also of course comment the services directly in the [docker-compose.yml](./docker-compose.yml) file.

### Develop in Bahmn Apps

Bahmni Docker project can be used to setup a dev environment for Bahmni. This is especially easy when working on Bahmni Apps.


This can be done by using `watch rsync ...` command to see your changes on the running server.
1. Clone and build Bahmni Apps locally:
```
cd ~/repos
git clone https://github.com/Bahmni/openmrs-module-bahmniapps.git
cd openmrs-module-bahmniapps/ui
```
Change JS and HTML files as you like.

2. Run the `watch rsync` command to override the server files: (using `watch` makes it run every 2 seconds)
```
watch rsync -av ~/repos/openmrs-module-bahmniapps/ui/ /tmp/bahmni-distro-haiti/bahmni_emr/bahmniapps/
```


### All environment variables


`OPENMRS_CONFIG_PATH`: Path to a custom OpenMRS Configuration. See [OpenMRS Initializer](https://github.com/mekomsolutions/openmrs-module-initializer/) for more information.

`BAHMNI_CONFIG_PATH`: Path to a custom Bahmni Config folder.

`OPENMRS_MODULES_PATH`: Path to custom set of OpenMRS modules.

`BAHMNI_APPS_PATH`: Path to Bahmni Apps sources.

`BAHMNI_HOME`: Path to Bahmni Home.

`TIMEZONE`**\***: Server timezone. See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a complete list of possible Timezones.

`BAHMNI_MART_CRON_TIME`**\***: Provide a custom cron time (in Crontab format) for the Bahmni Mart flattening. Default is `30 21 * * *` - i.e. 10:30 PM every day.

`ODOO_EXTRA_ADDONS`: Path to Odoo additional addons.

`ODOO_CONFIG_PATH`: Path to a custom Odoo Configuration. See [Odoo Initializer](https://github.com/mekomsolutions/
odoo-initializer/) for more informations.

**\*** Note: Variables with a **\*** require the containers to be rebuilt. Use `docker-compose build`


## Known limitations

- Supported components:
  - OpenMRS
  - Bahmni Apps
  - Bahmni Config
  - Bahmni Mart
  - Metabase
  - Odoo
  - Odoo Connect
