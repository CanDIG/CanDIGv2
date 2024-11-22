#!/usr/bin/env bash

# This script is meant to be run after make build-all, and checks whether
# the number of currently running docker containers matches the number of
# containers that should be running based on enabled services specified in .env.
# Also prints out all relevant logs from the error logging file (i.e., all lines
# that contain the phrases 'error' or 'warn').

python settings.py
source env.sh

RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
DEFAULT='\033[0m'

function print_module_logs() {
	MODULE=$1
	output=""
	BUILD_LINE=$(grep -n build-${MODULE} ${LOGFILE} | tail -1 | cut -d ':' -f 1)
	if [[ $BUILD_LINE != "" ]]; then
		LNO=$BUILD_LINE
		while read -r LINE; do
			if [[ $LINE == "Output of build-"* || $LINE == "Output of compose-"* ]]; then
				break
			else
				if [[ ${LINE} =~ .*([Ee]rror|[Ww]arn).* ]]; then
					output="${output}${GREEN}${LNO}${DEFAULT}	${LINE}\n"
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
					output="${output}${GREEN}${LNO}${DEFAULT}	${LINE}\n"
				fi
			fi
			LNO=$((LNO+1))
		done < <(tail -n "+$((COMPOSE_LINE+1))" $LOGFILE)
	fi
	if [[ $output != "" ]]; then
		printf "\n\n${RED}Error logs for ${MODULE}:\n--------------------\n${DEFAULT}"
		printf "${output}"
		printf "${RED}--------------------\n${DEFAULT}\n"
	fi
}

MODULES=$(cat .env | grep CANDIG_MODULES | cut -c 16- | cut -d '#' -f 1)
ALL_MODULES="${MODULES}"

EXPECTED_CONTAINERS=""
for MODULE in $ALL_MODULES; do
  services=$(cat lib/$MODULE/docker-compose.yml | yq -ojson '.services' | jq  'keys' | jq -r @sh | sed s/^\'/candigv2_/g | sed s/\'$/_1/g | sed "s/\'\ \'/_1\\ candigv2_/g" | sed "s/'\\s'/_1\\ candigv2_/g")
  EXPECTED_CONTAINERS=$(echo $EXPECTED_CONTAINERS $services)
  sc=$(cat lib/$MODULE/docker-compose.yml | yq -ojson '.services' | jq  'keys' | jq -r @sh | wc -w | tr -d ' ')
done

EXPECTED_COUNT=$(echo $EXPECTED_CONTAINERS | wc -w)

RUNNING_CONTAINERS=$(docker ps --format "{{.Names}}")
RUNNING_COUNT=$(echo $RUNNING_CONTAINERS | wc -w)

# figure out any containers that should've been there but aren't
for i in $EXPECTED_CONTAINERS
do
	[[ ! $RUNNING_CONTAINERS =~ $i  ]] && MISSING_CONTAINERS="${MISSING_CONTAINERS:+${MISSING_CONTAINERS} }$i"
done
# echo expected: $EXPECTED_CONTAINERS
# echo running: $RUNNING_CONTAINERS
# echo missing: $MISSING_CONTAINERS
if [[ $(echo $MISSING_CONTAINERS | wc -w | tr -d ' ') == "0"  ]]
then
	for MODULE in $ALL_MODULES; do
		print_module_logs $MODULE $COLOR
	done
	echo -e "${GREEN}Number of expected CanDIG services matches number of containers running!${DEFAULT} Lines above are in ${LOGFILE} and may be helpful for debugging."
 	exit 0
else
	for MODULE in $ALL_MODULES; do
		print_module_logs $MODULE
	done
	echo -e "${RED}WARNING: ${YELLOW}Some containers that are expected to be running are missing:\n${MISSING_CONTAINERS}
${DEFAULT}Lines above are in ${LOGFILE} and may be helpful for debugging."
	exit 1
fi
