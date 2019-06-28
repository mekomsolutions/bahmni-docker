# Bahmni-Docker
Dockerfile and resources to create Docker images for Bahmni

### Building a new image
This repository comes with a set of preset profiles to create a new Bahmni Docker image for the most common components used. See the [./inventories](./inventories) folder for a list of all inventory files available.
If the existing inventory files don't suit to your need, you can manually create a new one and start the image based on it.

#### Run the Docker build to build the new image
To build the Bahmni Docker image, just run the following instructions :
```
export file_name=[file_name]
export commit_id=[commit_id]
```

where:
- [file_name] is the name of the inventory file from inventories/ folder
- [commit_id] is the 7 first digits of your current commit.

```
git clone https://github.com/mekomsolutions/bahmni-docker.git
cd bahmni-docker/
docker build --build-arg INVENTORY_FILE=${file_name} ./ -t mekomsolutions/bahmni:${file_name}_${commit_id}_installer
docker container rm bahmni_${file_name}_${commit_id}_installer
docker run --privileged --name bahmni_${file_name}_${commit_id}_installer -v /sys/fs/cgroup:/sys/fs/cgroup:ro -d mekomsolutions/bahmni:${file_name}_installer
docker exec bahmni_${file_name}_${commit_id}_installer /tmp/install_bahmni.sh
docker commit -c='ENTRYPOINT ["/usr/sbin/init"]' bahmni_${file_name}_${commit_id}_installer mekomsolutions/bahmni_${file_name}_${commit_id}
```

To run the built Docker image, just run the following instructions:

```
docker run  --privileged --name [bahmni_container_name] -v /sys/fs/cgroup:/sys/fs/cgroup:ro -d mekomsolutions/bahmni_${file_name}_${commit_id}
docker exec [bahmni_container_name] /tmp/start_bahmni.sh
```


### Push the newly built image, if needed

To push the newly built Docker image:
```
docker push mekomsolutions/bahmni:[inventory_profile]_[commit_id]
```

Note that you would need to have logged in using `docker login` first