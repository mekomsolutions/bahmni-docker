FROM tomcat:7-jdk8-adoptopenjdk-hotspot

ARG BATCH_JAR_URL=https://nexus.mekomsolutions.net/repository/maven-releases/org/bahmni/batch/bahmni-endtb-batch/2.4.1/bahmni-endtb-batch-2.4.1.jar

RUN apt update && apt install -y wget
RUN mkdir -p /opt/batch/ && cd /opt/batch && wget ${BATCH_JAR_URL}

EXPOSE 8080
CMD java -DOPENMRS_DB_SERVER=${OPENMRS_DB_SERVER} -DOPENMRS_DB_USER=${OPENMRS_DB_USERNAME} -DOPENMRS_DB_PASSWORD=${OPENMRS_DB_PASSWORD} -jar /opt/batch/bahmni-endtb-batch-2.4.1.jar
