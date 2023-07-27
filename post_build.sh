#!/usr/bin/env bash

# This script is meant to be run after make build-all, and checks whether
# the number of currently running docker containers matches the number of 
# containers that should be running based on enabled services specified in .env. 
# Also prints out all relevant logs from the error logging file (i.e., all lines 
# that contain the phrases 'error' or 'warn').

source <(grep --color=never "ERRORLOG" .env)

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
			if [[ $LINE == "Output of build-"* || $LINE == "Output of compose-"* ]]; then
				break
			else
				if [[ ${LINE} =~ .*([Ee]rror|[Ww]arn).* ]]; then
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
			if [[ $LINE == "Output of build-"* || $LINE == "Output of compose-"* ]]; then
				break
			else
				if [[ ${LINE} =~ .*([Ee]rror|[Ww]arn).* ]]; then
					printf "${GREEN}${LNO}${DEFAULT}	${LINE}\n"
				fi
			fi
			LNO=$((LNO+1))
		done < <(tail -n "+$((COMPOSE_LINE+1))" $ERRORLOG)
	fi
}

MODULES=$(cat .env | grep CANDIG_MODULES | cut -c 16- | cut -d '#' -f 1)
MODULES_AUTH=$(cat .env | grep CANDIG_AUTH_MODULES | cut -c 21- | cut -d '#' -f 1)
ALL_MODULES="${MODULES}${MODULES_AUTH}"

# Note: drs-server is not currently built by the Makefile. Its values will need 
# to be changed when this is no longer the case.
SERVICE_COUNT=$(awk -v modules_raw="$ALL_MODULES" 'BEGIN {
	mcounts["candig-data-portal"]=1
	mcounts["federation"]=1
	mcounts["htsget"]=1
	mcounts["katsu"]=2
	mcounts["keycloak"]=1
	mcounts["logging"]=3
	mcounts["minio"]=1
	mcounts["monitoring"]=5
	mcounts["opa"]=2
	mcounts["toil"]=2
	mcounts["tyk"]=2
	mcounts["vault"]=2
	mcounts["candig-ingest"]=1
	mcounts["wes-server"]=1
	mcounts["drs-server"]=0
	split(modules_raw, modules, " ")
	service_count = 0
	for (module in modules) {
		service_count += mcounts[modules[module]]
	}
	print service_count
}')

RUNNING_MODULES=$(docker ps --format "{{.Names}}")

if [ $(docker ps -q | wc -l) == $SERVICE_COUNT ]
then
	for MODULE in $ALL_MODULES; do
		printf "\n\n${BLUE}Error logs for ${MODULE}:\n--------------------\n${DEFAULT}"
		print_module_logs $MODULE
		printf "${BLUE}--------------------\n${DEFAULT}"
	done
	echo -e "${GREEN}Number of expected CanDIG services matches number of containers running!${DEFAULT} Potentially useful error log segments listed above for debugging."
 	exit 0
else
	for MODULE in $ALL_MODULES; do
		printf "\n\n${RED}Error logs for ${MODULE}:\n--------------------\n${DEFAULT}"
		print_module_logs $MODULE
		printf "${RED}--------------------\n${DEFAULT}"
	done
	echo -e "${RED}WARNING: ${YELLOW}The number of CanDIG containers running does not match the number of expected services.\nRunning: ${BLUE}$(docker ps -q | wc -l) ${YELLOW}Expected: ${BLUE}${SERVICE_COUNT}
${DEFAULT}Check your build/docker logs. Potentially offending service logs shown above. View ${ERRORLOG} for more information."
	exit 1
fi
