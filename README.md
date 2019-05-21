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
```

**Build the components:**

- Bahmni Proxy
```
docker build -t bahmni-proxy ./bahmni-proxy
```

**Start Bahmni:**
```
docker-compose up
```

**Access the servers:**

OpenMRS server is accessible at http://localhost/openmrs

----

### Known limitations

- Only OpenMRS Component is supported for now.
