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
```

Note: After changing the Timezone - Run  ```docker-compose up --build```  to change the container's timezone (only applicable to bahmni-mart as of now)

**Start Bahmni:**
```
docker-compose up --build
```

**Access the servers:**

OpenMRS server is accessible at http://localhost/openmrs
Bahmni Apps Login page is accessible at http://localhost/bahmniapps/home/index.html

----

### Known limitations

- Supported components:
  - OpenMRS
  - Bahmni Apps
  - Bahmni Config
