# Bahmni Docker

Docker Compose project to start a Bahmni server locally.

### Quick Start

**Clone the project:**
```
git clone https://github.com/mekomsolutions/bahmni-docker
cd bahmni-docker
```

**Export the variable beforehand:**
```
export OPENMRS_MODULES_PATH="/path/to/the/openmrs/modules"
export BAHMNI_CONFIG_PATH="/path/to/the/bahmni/config"
export OPENMRS_CONFIG_PATH="/path/to/the/openmrs/config"
export BAHMNI_HOME="/path/to/the/bahmni/home"
export TIMEZONE="some/timezone" #Example for IST set TIMEZONE="Asia/Kolkata"
export CRON_TIME="CRON Formatted String" # This is to schedule database flattening. Default is "30 21 * * *" - i.e. 10:30 PM every day
```

Note: Complete list of available Timezone: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
After changing the Timezone, make sure to rebuild the containers with  ```docker-compose up --build```

**Start Bahmni:**
```
docker-compose up
```

**Access the servers:**

| Service | URL  | Remarks |
| --- | ---  | --- |
| Bahmni | http://localhost/  | Redirects to http://localhost/bahmni/home/index.html |
| OpenMRS | http://localhost/openmrs  |
| Metabase | http://localhost:9003/ or http://metabase.localhost  | Using the subdomain on other domains than `localhost` will require to set the `ServerName` variable accordingly in [000-proxy.conf](./bahmni_proxy/confs/000-proxy.conf)|


----

### Known limitations

- Supported components:
  - OpenMRS
  - Bahmni Apps
  - Bahmni Config
  - Bahmni Mart
  - Metabase
