# Interacting with the stack using Make

The [Makefile](Makefile) contains a number of make targets that make interacting the stack more user-friendly. All Makefile commands need to be run from the root directory of the CanDIGv2 repo.


## Stopping services

All services can be stopped with:

```bash
make stop-all
```

Individual services can be stopped using the docker command:
```bash

```

## Starting services

Logging must be started first, postgres should be started before any relying services

## Cleaning and rebuilding individual services

Any individual services can be cleaned with:

```bash
make clean-<name_of_module>
```

for example:

```bash
make clean-htsget
```

This stops the container, deletes the container and deletes the image (does it delete the actual data in postgres though?)

> [!NOTE]
> 

## Non-destructive Rebuild


To rebuild the CanDIGv2 without destroying data in postgres or keycloak the make target `rebuild-keep-data` with:

```bash
make rebuild-keep-data
```

> [!NOTE]
> If there are changes that have changed the structure of the database or impacted the versions of other CANDIG_DATA_MODULES this way of rebuilding cannot be used.

## Destructive Cleanup 

Use the following steps to clean up running CanDIGv2 services in a docker-compose configuration. 

> [!CAUTION] 
> Note that these steps are destructive and will remove **ALL** containers, secrets, volumes, networks, certs, and images. If you are using docker in a shared environment (i.e. with other non-CanDIGv2 containers running) please consider running the cleanup steps manually instead.

The following steps are performed by `make clean-all`:

```bash
# 1. stop and remove running stacks
make clean-compose

# 2. stop and remove remaining containers
make clean-containers

# 3. remove all configs/secrets from docker and local dir
make clean-secrets

# 4. remove all docker volumes and local data dir
make clean-volumes

# 5. delete all cached images
make clean-images
```

## Rebuild stack from scratch


