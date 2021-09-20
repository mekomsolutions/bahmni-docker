# Bahmni Docker

Resources to build to Docker images needed to run Bahmni

<p align="left">
  <img src="./readme/bahmni-logo-square.png" alt="Bahmni Logo" height="155">
  <img src="./readme/plus.png" alt="plus sign" height="50">
  <img src="./readme/vertical-logo-monochromatic.png" alt="Docker Logo" height="150">
  </p>

## Build and deploy images

Each image can be built individually by doing:

Eg, Bahmni Appointments:
```
cd appointments/
docker build . -t mekomsolutions/appointments:bahmni_latest
docker push mekomsolutions/appointments:bahmni_latest
```

## GitHub CI

GitHub Actions will build and push all images upon new commits.
See [build.yml/](.github/workflows/build.yml)
