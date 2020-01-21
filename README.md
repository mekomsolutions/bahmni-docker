# Bahmni Docker

Docker Compose project to start a Bahmni server locally.

### Quick Start

#### Clone the project:
```
git clone https://github.com/mekomsolutions/bahmni-docker
cd bahmni-docker
```

#### Export the variable beforehand:

Here is the list of configurable variables:

`OPENMRS_CONFIG_PATH`: Path to a custom OpenMRS Configuration. See [OpenMRS Initializer](https://github.com/mekomsolutions/openmrs-module-initializer/) for more information.

`BAHMNI_CONFIG_PATH`: Path to a custom Bahmni Config folder.

`OPENMRS_MODULES_PATH`: Path to custom set of OpenMRS modules.

`BAHMNI_HOME`: Path to Bahmni Home.

`TIMEZONE`**\***: Server timezone. See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a complete list of possible Timezones. Default

`BAHMNI_MART_CRON_TIME`**\***: Provide a custom cron time (in Crontab format) for the Bahmni Mart flattening. Default is `30 21 * * *` - i.e. 10:30 PM every day.

**\*** Note: Variables with a **\*** require the containers to be rebuilt. Use `docker-compose build`

#### Start Bahmni:
```
docker-compose up
```

#### Access the servers:

- Bahmni: http://localhost/
- OpenMRS: http://localhost/openmrs
- Metabase: http://localhost:9003/

#### TLS support

By default, TLS is enabled with self-signed certificates.
You can provide your own valid certificates as a volume mounted at `/etc/tls/`.

Eg:
```
volumes:
  - "/etc/letsencrypt/live/domain.com/:/etc/tls/"

```


To deactivate TLS support, just remove the entire line:
```command: "httpd-foreground -DenableTLS"``` from the `proxy` service in the Dockerfile


----

### Known limitations

- Supported components:
  - OpenMRS
  - Bahmni Apps
  - Bahmni Config
  - Bahmni Mart
  - Metabase
