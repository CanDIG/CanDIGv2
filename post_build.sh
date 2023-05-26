#!/usr/bin/env bash

# This script is meant to be run after make build-all, and checks whether
# the number of currently running docker containers matches the number of 
# containers that should be running based on enabled services specified in .env. 
# Also prints out all relevant logs from the error logging file (i.e., all lines 
# that contain the phrases 'error' or 'warn').

ERRORLOG="tmp/error.txt"

RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
DEFAULT='\033[0m'

function print_module_logs() {
	MODULE=$1
	BUILD_LINE=$(grep -n build-${MODULE} ${ERRORLOG} | tail -1 | cut -d ':' -f 1)
	if [[ $BUILD_LINE != "" ]]; then
		LNO=$BUILD_LINE
		while read -r LINE; do
			if [[ $LINE == "Errors during build-"* || $LINE == "Errors during compose-"* ]]; then
				break
			else
				if [[ ${LINE,,} =~ .*(error|warn).* ]]; then
					printf "${GREEN}${LNO}${DEFAULT}	${LINE}\n"
				fi
			fi
			LNO=$((LNO+1))
		done < <(tail -n "+$((BUILD_LINE + 1))" $ERRORLOG)
	fi
	COMPOSE_LINE=$(grep -n compose-${MODULE} ${ERRORLOG} | tail -1 | cut -d ':' -f 1)
	if [[ $COMPOSE_LINE != "" ]]; then
		LNO=$COMPOSE_LINE
		while read -r LINE; do
			if [[ $LINE == "Errors during build-"* || $LINE == "Errors during compose-"* ]]; then
				break
			else
				if [[ ${LINE,,} =~ .*(error|warn).* ]]; then
					printf "${GREEN}${LNO}${DEFAULT}	${LINE}\n"
				fi
			fi
			LNO=$((LNO+1))
		done < <(tail -n "+$((COMPOSE_LINE+1))" $ERRORLOG)
	fi
}


declare -A MODULE_COUNTS

# Note: drs-server is not currently built by the Makefile. Its values will need 
# to be changed when this is no longer the case.
MODULE_COUNTS=( ["candig-data-portal"]=1 ["federation"]=1 ["htsget"]=1
				["katsu"]=2 ["keycloak"]=1 ["logging"]=3 ["minio"]=1 ["monitoring"]=5
				["opa"]=2 ["toil"]=2 ["tyk"]=2 ["vault"]=2 ["wes-server"]=1 ["drs-server"]=0 )
				
SERVICE_COUNT=0

MODULES=$(cat .env | grep CANDIG_MODULES | cut -c 16- | cut -d '#' -f 1)
MODULES_AUTH=$(cat .env | grep CANDIG_AUTH_MODULES | cut -c 21- | cut -d '#' -f 1)
ALL_MODULES="${MODULES}${MODULES_AUTH}"

for MODULE in $ALL_MODULES; do
	MODULE_SERVICES=${MODULE_COUNTS[$MODULE]}
	SERVICE_COUNT=$((SERVICE_COUNT + MODULE_SERVICES))
done

if [ $(docker ps -q | wc -l) == $SERVICE_COUNT ]
then
	echo -e "${GREEN}Number of expected CanDIG services matches number of containers running!${DEFAULT}"
else
	RUNNING_MODULES=$(docker ps --format "{{.Names}}")
	for MODULE in $ALL_MODULES; do
		printf "\n\n${RED}Error logs for ${MODULE}:\n--------------------\n${DEFAULT}"
		print_module_logs $MODULE
		printf "${RED}--------------------\n${DEFAULT}"
	done
	echo -e "${RED}WARNING: ${YELLOW}The number of CanDIG containers running does not match the number of expected services.\nRunning: ${BLUE}$(docker ps -q | wc -l) ${YELLOW}Expected: ${BLUE}${SERVICE_COUNT}
${DEFAULT}Check your build/docker logs. Potentially offending service logs shown above. View ${ERRORLOG} for more information."
fi
