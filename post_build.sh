#!/usr/bin/env bash

RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
DEFAULT='\033[0m'

declare -A MODULE_COUNTS

# Note: Logging, drs-server and wes-server are not currently built by
# the Makefile. Their values will need to be changed when this is no
# longer the case.
MODULE_COUNTS=( ["candig-data-portal"]=1 ["federation"]=1 ["htsget"]=1
				["katsu"]=2 ["keycloak"]=1 ["logging"]=3 ["minio"]=1 ["monitoring"]=5
				["opa"]=2 ["toil"]=2 ["tyk"]=2 ["vault"]=2 ["wes-server"]=1 ["drs-server"]=0 )
				
SERVICE_COUNT=0

MODULES=$(cat .env | grep CANDIG_MODULES | cut -c 16- | cut -d '#' -f 1)
	
for MODULE in $MODULES; do
	MODULE_SERVICES=${MODULE_COUNTS[$MODULE]}
	SERVICE_COUNT=$((SERVICE_COUNT + MODULE_SERVICES))
done

MODULES_AUTH=$(cat .env | grep CANDIG_AUTH_MODULES | cut -c 21- | cut -d '#' -f 1)
for MODULE in $MODULES_AUTH; do
	MODULE_SERVICES=${MODULE_COUNTS[$MODULE]}
	SERVICE_COUNT=$((SERVICE_COUNT + MODULE_SERVICES))
done

if [ $(docker ps -q | wc -l) == $SERVICE_COUNT ]
then
	echo -e "${GREEN}Number of expected CanDIG services matches number of containers running!${DEFAULT}"
else
	echo -e "${RED}WARNING: ${YELLOW}The number of CanDIG containers running does not match the number of expected services.\nRunning: ${BLUE}$(docker ps -q | wc -l) ${YELLOW}Expected: ${BLUE}${SERVICE_COUNT}
${DEFAULT}Check your build/docker logs."
fi
