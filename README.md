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
export CRON_TIME=<CRON Formatted String> # This is to schedule mart cron. Default is "30 21 * * *" - i.e. 10:30 PM every day
```

Note: After changing the Timezone - Run  ```docker-compose up --build```  to change the container's timezone (only applicable to bahmni-mart as of now)

**Start Bahmni:**
```
docker-compose up --build
```

**Access the servers:**

OpenMRS server is accessible at http://localhost/openmrs
Bahmni Apps Login page is accessible at http://localhost/bahmniapps/home/index.html
Metabase is accessible by port - localhost:9003 or by subdomain metabase.localhost

----

### Known limitations

- Supported components:
  - OpenMRS
  - Bahmni Apps
  - Bahmni Config
