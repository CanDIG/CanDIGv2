#!/usr/bin/env bash

# This script is used for CanDIG Github Actions to grab all docker container
# logs for further inspection.

CONTAINERS=$(docker ps -a --format "{{.Names}}")
for CONTAINER in $CONTAINERS; do
	echo "Container logs for ${CONTAINER}:"
	docker logs ${CONTAINER}
	printf "\n\n"
done
