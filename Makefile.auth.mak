#>>>
# close all authentication and authorization services

#<<<
clean-auth:
	cat $(DIR)/lib/compose/docker-compose.yml $(DIR)/lib/logging/$(DOCKER_LOG_DRIVER)/docker-compose.yml \
		$(DIR)/lib/authentication/docker-compose.yml | docker-compose -f - down

	cat $(DIR)/lib/compose/docker-compose.yml $(DIR)/lib/logging/$(DOCKER_LOG_DRIVER)/docker-compose.yml \
		$(DIR)/lib/authorization/docker-compose.yml | docker-compose -f - down
	
	# - remove intermittent docker images
	# -- authentication
	docker rmi candigv2_keycloak:latest --force
	docker rmi candigv2_tyk:latest --force
	# -- authorization
	docker rmi candigv2_vault:latest --force
	docker rmi candigv2_candig-server-authorization:latest --force

	# closes the candig server along with its corresponding arbiter and opa
	docker-compose -f ${PWD}/lib/compose/docker-compose.yml -f $(DIR)/lib/candig-server/docker-compose.yml down


#TODO: deprecate compose-authx-clean
#>>>
# dismantle and remove all data of
# candig-server prototype instances with authentication
# and authorization services

#<<<
compose-authx-clean: compose-authx-down
	# clean keycloak
	docker volume rm candigv2_keycloak-data
	# clean tyk
	docker volume rm candigv2_tyk-data
	docker volume rm candigv2_tyk-redis-data
	# clean vault
	docker volume rm candigv2_vault-data


#>>>
# create instances of authentication and
# authorization services

#<<<
#TODO: deprecate this method
#TODO: use init-auth to set up auth stack
#TODO: move data directories to tmp/ instead of lib/

.PHONY: init-auth
init-auth:
	echo "    started init-auth" >> $(LOGFILE)

#>>>
# create instances of authentication and
# authorization services

#<<<
#TODO: deprecate this method
#TODO: use init-auth to set up auth stack
#TODO: move data directories to tmp/ instead of lib/

compose-authx-setup:
	# # sets up keycloak, tyk, vault, a candig-server-arbiter, and a candig-server-authorization
	echo

	mkdir -p ${PWD}/lib/authentication/keycloak
	mkdir -p ${PWD}/lib/authentication/tyk

	mkdir -p ${PWD}/lib/authorization/vault


	# Generate dynamic environment variables
	$(eval KEYCLOAK_CLIENT_ID_64=$(shell echo -n $(KEYCLOAK_CLIENT_ID) | base64))

	# temp: in production, explicitly indicating port 443 breaks vaults internal oidc provider checks.
	# simply remove the ":443 from the authentication services public url for this purpose:
	if [[ ${KEYCLOAK_PUBLIC_URL} == *":443"* ]]; then \
		echo "option 1"; \
		$(eval TEMP_KEYCLOAK_PUBLIC_URL=$(shell echo ${KEYCLOAK_PUBLIC_URL} | sed -e 's/\(:443\)\$//g')) \
	elif [[ ${KEYCLOAK_PUBLIC_URL} == *":80"* ]]; then \
		echo "option 2"; \
		$(eval TEMP_KEYCLOAK_PUBLIC_URL=$(shell echo ${KEYCLOAK_PUBLIC_URL} | sed -e 's/\(:80\)\$//g')) \
	else \
		echo "option 3"; \
		$(eval TEMP_KEYCLOAK_PUBLIC_URL=$(shell echo ${KEYCLOAK_PUBLIC_URL})) \
	fi


	# inject dynamic variables in a "Makefile-ish" way
	# by chaining these calls "all in one line" so that
	# variables properly get exported from each sub script
	# and propogate to the next ones
	export KEYCLOAK_CLIENT_ID_64=$(KEYCLOAK_CLIENT_ID_64); \
	export TEMP_KEYCLOAK_PUBLIC_URL=$(TEMP_KEYCLOAK_PUBLIC_URL); \
	\
	echo ; \
	if [[ ${AUTHN_USE_LOCAL_IDP} == 1 ]]; then \
		echo "Setting up Keycloak;" ; \
		source ${PWD}/etc/setup/scripts/subtasks/keycloak_setup.sh; \
	fi ; \
	echo ; \
	echo "Setting up Tyk;" ; \
	${PWD}/etc/setup/scripts/subtasks/tyk_setup.sh; \
	echo ; \
	echo "Setting up Vault;" ; \
	source ${PWD}/etc/setup/scripts/subtasks/vault_setup.sh; \
	echo ; \
	echo "Setting up OPAs;" ; \
	${PWD}/etc/setup/scripts/subtasks/opa_setup.sh ; \
	echo ; \
	echo "Setting up Arbiters;" ; \
	${PWD}/etc/setup/scripts/subtasks/arbiter_setup.sh


	# clean up
	echo
	echo "Moving temporary files to ${PWD}/tmp/authorization/*"
	mkdir -p ${PWD}/tmp/configs/authentication
	mkdir -p ${PWD}/tmp/configs/authorization

	cp -r ${PWD}/lib/authentication/keycloak/tmp ${PWD}/tmp/configs/authentication/keycloak/
	cp -r ${PWD}/lib/authentication/tyk/tmp ${PWD}/tmp/configs/authentication/tyk/

	cp -r ${PWD}/lib/authorization/vault/tmp ${PWD}/tmp/configs/authorization/vault/
	cp -r ${PWD}/lib/candig-server/authorization/tmp ${PWD}/tmp/configs/authorization/candig-server

	rm -rf ${PWD}/lib/authentication/*/tmp
	rm -rf ${PWD}/lib/authorization/*/tmp
	rm -rf ${PWD}/lib/candig-server/authorization/tmp


	echo
	echo "-- authorization Setup Done! --"
	echo


#>>>
# create an instance of a candig-server prototype
# with authentication and authorization services

#<<<
#TODO: deprecate compose-authx-setup-candig-server
compose-authx-setup-candig-server: compose-authx-setup
	# intended to run candig server alongside the authx modules
	#docker-compose -f ${DIR}/lib/compose/docker-compose.yml -f $(DIR)/lib/candig-server/docker-compose.yml up -d candig-server 2>&1

	export SERVICE=candig-server && $(MAKE) compose-candig-server

#>>>
# run authentication and authorization
# tests with both chrome and firefox front-ends

#<<<
#TODO: fix broken tests
#test-authx-prototype:
	#$(DIR)/etc/tests/integration/authx/run_tests.sh 20 chrome True
	#$(DIR)/etc/tests/integration/authx/run_tests.sh 20 firefox True

