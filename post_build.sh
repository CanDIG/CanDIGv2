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
ALL_MODULES="${MODULES}"

SERVICE_COUNT=0
for MODULE in $ALL_MODULES; do
  sc=$(cat lib/$MODULE/docker-compose.yml | yq -ojson '.services' | jq  'keys' | jq -r @sh | wc -w | tr -d ' ')
  SERVICE_COUNT=`expr $SERVICE_COUNT + $sc`
done

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
