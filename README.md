# Bahmni Docker

Docker Compose project to start a Bahmni server locally.

<p align="left">
  <img src="./readme/vertical-logo-monochromatic.png" alt="Docker" height="150"> +  
  <img src="./readme/bahmni-logo-square.png" alt="Docker" height="155">  
</p>

----
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

For a more detailed list of variables:

`OPENMRS_CONFIG_PATH`: Path to a custom OpenMRS Configuration. See [OpenMRS Initializer](https://github.com/mekomsolutions/openmrs-module-initializer/) for more information.

`BAHMNI_CONFIG_PATH`: Path to a custom Bahmni Config folder.

`OPENMRS_MODULES_PATH`: Path to custom set of OpenMRS modules.

`BAHMNI_APPS_PATH`: Path to Bahmni Apps sources.

`BAHMNI_HOME`: Path to Bahmni Home.

`TIMEZONE`**\***: Server timezone. See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a complete list of possible Timezones.

`BAHMNI_MART_CRON_TIME`**\***: Provide a custom cron time (in Crontab format) for the Bahmni Mart flattening. Default is `30 21 * * *` - i.e. 10:30 PM every day.

**\*** Note: Variables with a **\*** require the containers to be rebuilt. Use `docker-compose build`

### Start Bahmni:
```
docker-compose up
```

### Access the servers:

- Bahmni: http://localhost/
- OpenMRS: http://localhost/openmrs
- Metabase: http://localhost:9003/

----

## Advanced

### TLS support

To enable TLS support, just add the line:

```
  command: "httpd-foreground -DenableTLS"
```
to the `proxy` service in the [docker-compose.yml](./docker-compose.yml) file.

Default certificates are self-signed.

Provide your own valid certificates as a bound volume mounted at `/etc/tls/`.

This would look like:
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




### Disable individual services
If you are developing, you may not want to run the complete Bahmni suite.
You can disable services by adding a new **docker-compose.override.yml** at the project root with the following contents:

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

You can also commenting the services directly in the [docker-compose.yml](./docker-compose.yml) file.

### Develop in Bahmn Apps

You can use the Bahmni Docker project to setup your dev environment for Bahmni. This is especially easy when working on Bahmni Apps.

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
----

### Known limitations

- Supported components:
  - OpenMRS
  - Bahmni Apps
  - Bahmni Config
  - Bahmni Mart
  - Metabase
