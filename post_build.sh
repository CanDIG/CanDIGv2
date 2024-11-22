#!/usr/bin/env bash

# This script is meant to be run after make build-all, and checks whether
# the number of currently running docker containers matches the number of
# containers that should be running based on enabled services specified in .env.
# Also prints out all relevant logs from the error logging file (i.e., all lines
# that contain the phrases 'error' or 'warn').

source <(grep --color=never "LOGFILE" .env)

RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
DEFAULT='\033[0m'

function print_module_logs() {
	MODULE=$1
	BUILD_LINE=$(grep -n build-${MODULE} ${LOGFILE} | tail -1 | cut -d ':' -f 1)
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
		done < <(tail -n "+$((BUILD_LINE + 1))" $LOGFILE)
	fi
	COMPOSE_LINE=$(grep -n compose-${MODULE} ${LOGFILE} | tail -1 | cut -d ':' -f 1)
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
		done < <(tail -n "+$((COMPOSE_LINE+1))" $LOGFILE)
	fi
}

MODULES=$(cat .env | grep CANDIG_MODULES | cut -c 16- | cut -d '#' -f 1)
ALL_MODULES="${MODULES}"

EXPECTED_CONTAINERS=""
for MODULE in $ALL_MODULES; do
  services=$(cat lib/$MODULE/docker-compose.yml | yq -ojson '.services' | jq  'keys' | jq -r @sh | sed s/\'//g)
  EXPECTED_CONTAINERS=$(echo $EXPECTED_CONTAINERS $services)
  sc=$(cat lib/$MODULE/docker-compose.yml | yq -ojson '.services' | jq  'keys' | jq -r @sh | wc -w | tr -d ' ')
done

EXPECTED_COUNT=$(echo $EXPECTED_CONTAINERS | wc -w)

RUNNING_CONTAINERS=$(docker ps --format "{{.Names}}" | sed s/candigv2_//g | sed s/_1//g)
RUNNING_COUNT=$(echo $RUNNING_CONTAINERS | wc -w)

# figure out any containers that should've been there but aren't
for i in $EXPECTED_CONTAINERS
do
	[[ ! $RUNNING_CONTAINERS =~ $i  ]] && MISSING_CONTAINERS="${MISSING_CONTAINERS:+${MISSING_CONTAINERS} }$i"
done

if [[ $(echo $MISSING_CONTAINERS | wc -w | tr -d ' ') == "0"  ]]
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
	echo -e "${RED}WARNING: ${YELLOW}Some containers that are expected to be running are missing:\n${MISSING_CONTAINERS}
${DEFAULT}Check your build/docker logs. Potentially offending service logs shown above. View ${LOGFILE} for more information."
	exit 1
fi
