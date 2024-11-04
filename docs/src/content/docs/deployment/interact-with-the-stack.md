---
title: Interacting with the stack using Make
description: A guide to using make commands to interact with the stack
---

The [Makefile](Makefile) contains a number of make targets that make interacting the stack more user-friendly. All Makefile commands need to be run from the root directory of the CanDIGv2 repo.

## Stopping services

All services can be stopped with:

```bash
make stop-all
```

Individual services can be stopped using the docker command:
```bash
docker container stop candigv2_<name of module>_1
```

eg. to stop the ingest container this would be:
```bash
docker container stop candigv2_candig-ingest_1
```

## Starting services

Logging must be started first, postgres should be started before any relying services

When all containers are stopped the following command can be used to start all CanDIGv2 containers

```bash
make start-all
```

To start a single container, the following docker command can be used:

```bash
docker container start candigv2_<name of module>_1
```
e.g. for the ingest container:
```bash
docker container start candigv2_candig-ingest_1
```

## Cleaning and rebuilding individual services

If any individual services are updated, they will need to be cleaned, rebuilt and recomposed. 

Any individual service can be cleaned with:

```bash
make recompose-<name of module>
```

This command runs all the steps needed to clean and rebuild the service, the commands are explained in more detail below:

```bash
make clean-<name of module>
```

for example:

```bash
make clean-htsget
```

This stops the container, deletes the container and deletes the image.

:::note
For services that use the postgres container to save data, i.e. htsget (genomic data) and katsu (clinical data), deleting and rebuilding the service will not delete the data in postgres. If there have been changes to the underlying database, the postgres database will need to be deleted and rebuilt. 
:::

To rebuild and recompose a service first run:

```bash
make build-<name of module>
```

:::note
Containers that have an associated volume will need to have the volume rebuild with `make docker-volumes` before being able to successfully compose the container.
:::

Then compose the container with:

```bash
make compose-<name of module>
```

:::important
Some services can't be rebuilt individually without causing issues with the stack, if you are facing issues with modules related to auth, it is recommended to rebuild the entire stack to ensure everything is in sync.
:::

## Non-destructive Rebuild

To rebuild the CanDIGv2 without destroying data in postgres or keycloak the make target `rebuild-keep-data` with:

```bash
make rebuild-keep-data
```

:::note
If there are changes that have changed the structure of the database or impacted the versions of other `CANDIG_DATA_MODULES` this way of rebuilding cannot be used.
:::

## Destructive Cleanup 

Use the following steps to clean up running CanDIGv2 services in a docker-compose configuration. 

:::caution 
Note that these steps are destructive and will remove **ALL** logs, containers, secrets, volumes, networks, certs, and images. If you are using docker in a shared environment (i.e. with other non-CanDIGv2 containers running) please consider running the cleanup steps manually instead.
:::

The following steps are performed by `make clean-all`:

```bash
# 1. delete log files
make clean-logs

# 2. stop and remove running stacks
make clean-compose

# 3. stop and remove remaining containers
make clean-containers

# 4. remove all configs/secrets from docker and local dir
make clean-secrets

# 5. remove all docker volumes and local data dir
make clean-volumes

# 6. delete all cached images
make clean-images
```

See the [Makefile](../Makefile) for the exact commands that each of these targets runs.

## Rebuild entire stack from scratch

1. Perform any backups of data necessary if in a non-testing environment. (see [backup and restore doc](backup-restore-candig.md) for detailed instructions.)

2. Clean up the current containers with `make clean-all`

3. When complete, build all containers again with `make build-all`
