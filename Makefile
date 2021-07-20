#!make

#TODO: make debug optional
# import global variables
env ?= .env

include $(env)
export $(shell sed 's/=.*//' $(env))

SHELL = bash
DIR = $(PWD)
CONDA = $(DIR)/bin/miniconda3/condabin/conda
LOGFILE=$(DIR)/tmp/progress.txt

ifdef OVERRIDE_REGISTRY
	export DOCKER_REGISTRY = $(OVERRIDE_REGISTRY)
endif

.PHONY: all
all:
	@echo "CanDIGv2 Makefile Deployment"
	@echo "Type 'make help' to view available options"
	@echo "View README.md for additional information"

#>>>
# create non-repo directories
# make mkdir

#<<<
.PHONY: mkdir
mkdir:
	mkdir -p $(DIR)/bin
	mkdir -p $(DIR)/tmp/configs
	mkdir -p $(DIR)/tmp/data
	mkdir -p $(DIR)/tmp/secrets
	mkdir -p $(DIR)/tmp/ssl
	mkdir -p $(DIR)/tmp/authentication/{keycloak,tyk}
	mkdir -p $(DIR)/tmp/authorization/vault

#>>>
# download all package binaries
# make bin-all

#<<<
.PHONY: bin-all
bin-all: bin-conda bin-docker-machine bin-kompose bin-kubectl \
	bin-minikube bin-minio bin-traefik bin-prometheus

#>>>
# download miniconda package
# make bin-conda

#<<<
bin-conda: mkdir
	echo "    started bin-conda" >> $(LOGFILE)
ifeq ($(VENV_OS), linux)
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
endif
ifeq ($(VENV_OS), darwin)
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
endif
	bash $(DIR)/bin/miniconda_install.sh -f -b -u -p $(DIR)/bin/miniconda3
	echo "    finished bin-conda" >> $(LOGFILE)

#>>>
# download docker-machine (for swarm deployment)
# make bin-docker-machine

#<<<
bin-docker-machine: mkdir
	echo "    started bin-docker-machine" >> $(LOGFILE)
	curl -Lo $(DIR)/bin/docker-machine \
		https://github.com/docker/machine/releases/download/v0.16.2/docker-machine-`uname -s`-`uname -m`
	chmod 755 $(DIR)/bin/docker-machine
	echo "    finished bin-docker-machine" >> $(LOGFILE)

#>>>
# download kompose (for kubernetes deployment)
# make bin-kompose

#<<<
bin-kompose: mkdir
	echo "    started bin-kompose" >> $(LOGFILE)
	curl -Lo $(DIR)/bin/kompose \
		https://github.com/kubernetes/kompose/releases/download/v1.21.0/kompose-$(VENV_OS)-amd64
	chmod 755 $(DIR)/bin/kompose
	echo "    finished bin-kompose" >> $(LOGFILE)

#>>>
# download latest kubectl (for kubernetes deployment)
# make bin-kubectl

#<<<
bin-kubectl: mkdir
	echo "    started bin-kubectl" >> $(LOGFILE)
	curl -Lo $(DIR)/bin/kubectl \
		https://storage.googleapis.com/kubernetes-release/release/v1.18.6/bin/$(VENV_OS)/amd64/kubectl
	chmod 755 $(DIR)/bin/kubectl
	echo "    finished bin-kubectl" >> $(LOGFILE)

#>>>
# download latest minikube binary from Google repo
# make bin-minikube

#<<<
bin-minikube: mkdir
	echo "    started bin-minikube" >> $(LOGFILE)
	curl -Lo $(DIR)/bin/minikube \
		https://storage.googleapis.com/minikube/releases/latest/minikube-$(VENV_OS)-amd64
	chmod 755 $(DIR)/bin/minikube
	echo "    finished bin-minikube" >> $(LOGFILE)

#>>>
# download latest minio server/client from Minio repo
# make bin-minio

#<<<
bin-minio: mkdir
	echo "    started bin-minio" >> $(LOGFILE)
	curl -Lo $(DIR)/bin/minio \
		https://dl.minio.io/server/minio/release/$(VENV_OS)-amd64/minio
	curl -Lo $(DIR)/bin/mc \
		https://dl.minio.io/client/mc/release/$(VENV_OS)-amd64/mc
	chmod 755 $(DIR)/bin/minio
	chmod 755 $(DIR)/bin/mc
	echo "    finished bin-minio" >> $(LOGFILE)

#>>>
# download prometheus binaries from Github repo
# make bin-prometheus

#<<<
bin-prometheus:
	echo "    started bin-prometheus" >> $(LOGFILE)
	mkdir -p $(DIR)/bin/prometheus
	curl -Lo $(DIR)/bin/prometheus/prometheus.tar.gz \
		https://github.com/prometheus/prometheus/releases/download/v$(PROMETHEUS_VERSION)/prometheus-$(PROMETHEUS_VERSION).$(VENV_OS)-amd64.tar.gz
	tar --strip-components=1 -zxvf $(DIR)/bin/prometheus/prometheus.tar.gz -C $(DIR)/bin/prometheus
	chmod 755 $(DIR)/bin/prometheus/prometheus
	echo "    finished bin-prometheus" >> $(LOGFILE)

#>>>
# download latest traefik binary from Github repo
# make bin-traefik

#<<<
bin-traefik: mkdir
	echo "    started bin-traefik" >> $(LOGFILE)
	curl -Lo $(DIR)/bin/traefik.tar.gz \
		https://github.com/traefik/traefik/releases/download/v$(TRAEFIK_VERSION)/traefik_v$(TRAEFIK_VERSION)_$(VENV_OS)_amd64.tar.gz
	tar -xvzf $(DIR)/bin/traefik.tar.gz -C bin/
	chmod 755 $(DIR)/bin/traefik
	echo "    finished bin-traefik" >> $(LOGFILE)

#>>>
# (re)build service image and deploy/test using docker-compose
# $module is the name of the sub-folder in lib/
# add BUILD_OPTS='--no-cache' to ignore cached builds
# BUILD_OPTS='--no-cache' make build-$module
# make build-$module

#<<<
build-%:
	echo "    started build-$*" >> $(LOGFILE)
	DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 \
	cat $(DIR)/lib/compose/docker-compose.yml $(DIR)/lib/logging/$(DOCKER_LOG_DRIVER)/docker-compose.yml $(DIR)/lib/$*/docker-compose.yml \
		| docker-compose -f - build $(BUILD_OPTS)
	echo "    finished build-$*" >> $(LOGFILE)

#>>>
# run all cleanup functions
# WARNING: these are distructive steps, read through instructions before using
# make clean-all

#<<<
.PHONY: clean-all
clean-all: clean-stack clean-compose clean-containers clean-secrets clean-configs \
	clean-volumes clean-networks clean-images clean-swarm clean-machines \
	clean-certs clean-conda clean-bin

#>>>
# clear downloaded binaries
# removes $PWD/bin/
# make clean-bin

#<<<
.PHONY: clean-bin
clean-bin:
	rm -rf $(DIR)/bin

#>>>
# removed selfsigned-certs (including root-ca)
# make clean-certs

#<<<
.PHONY: clean-certs
clean-certs:
	rm -f $(DIR)/tmp/ssl/selfsigned-*

#>>>
# stops and removes docker-compose instances
# make clean-compose

#<<<
.PHONY: clean-compose
clean-compose:
	$(foreach MODULE, $(CANDIG_MODULES), \
		cat $(DIR)/lib/compose/docker-compose.yml $(DIR)/lib/logging/$(DOCKER_LOG_DRIVER)/docker-compose.yml $(DIR)/lib/$(MODULE)/docker-compose.yml \
		| docker-compose -f - down;)

#>>>
# deactivate and remove conda env $VENV_NAME
# make clean-conda

#<<<
.PHONY: clean-conda
clean-conda:
	$(CONDA) deactivate
	$(CONDA) env remove -n $(VENV_NAME)

#>>>
# clear swarm configs and remove config files
# make clean-configs

#<<<
.PHONY: clean-configs
clean-configs:
	-docker config rm `docker config ls -q`
	rm -rf $(DIR)/tmp/configs

#>>>
# stop all running containers and remove all stopped containers
# make clean-containers

#<<<
.PHONY: clean-containers
clean-containers:
	-docker stop `docker ps -q`
	docker container prune -f

#>>>
# clear all images (including base images)
# make clean-images

#<<<
.PHONY: clean-images
clean-images:
	docker image prune -a -f

#>>>
# shutdown kubernetes services
# make clean-kubernetes

#<<<
.PHONY: clean-kubernetes
clean-kubernetes:
	$(DIR)/bin/kompose --file $(DIR)/lib/kubernetes/docker-compose.yml \
		$(foreach MODULE, $(CANDIG_MODULES), --file $(DIR)/lib/$(MODULE)/docker-compose.yml) \
		down

#>>>
# destroy docker-machine cluster
# make clean-machines

#<<<
.PHONY: clean-machines
clean-machines:
	$(DIR)/bin/docker-machine rm -f `$(DIR)/bin/docker-machine ls -q`

#>>>
# destroy minikube cluster
# make clean-minikube

#<<<
.PHONY: clean-minikube
clean-minikube:
	$(DIR)/bin/minikube delete

#>>>
# remove all unused networks
# make clean-networks

#<<<
.PHONY: clean-networks
clean-networks:
	docker network prune -f

#>>>
# clear swarm secrets and remove secret files
# make clean-secrets

#<<<
.PHONY: clean-secrets
clean-secrets:
	-docker secret rm `docker secret ls -q`
	rm -rf $(DIR)/tmp/secrets

#>>>
# remove all stacks
# make clean-stack

#<<<
.PHONY: clean-stack
clean-stack:
	-docker stack rm `docker stack ls | awk '{print $$1}'`

#>>>
# leave docker-swarm
# make clean-swarm

#<<<
.PHONY: clean-swarm
clean-swarm:
	docker swarm leave --force

#>>>
# clear all tox screen sessions
# make clean-tox

#<<<
.PHONY: clean-tox
clean-tox:
	screen -ls | grep pts | cut -d. -f1 | awk '{print $$1}' | xargs kill

#>>>
# remove all peristant volumes and local data
# make clean-volumes

#<<<
.PHONY: clean-volumes
clean-volumes:
	-docker volume rm `docker volume ls -q`
	rm -rf $(DIR)/tmp/data

#>>>
# deploy/test all modules in $CANDIG_MODULES using docker-compose
# make compose

#<<<
.PHONY: compose
compose:
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) compose-$(MODULE);)
	# cat $(DIR)/lib/compose/docker-compose.yml $(DIR)/lib/logging/$(DOCKER_LOG_DRIVER)/docker-compose.yml \
	# 	$(foreach MODULE, $(CANDIG_MODULES), $(DIR)/lib/$(MODULE)/docker-compose.yml) \
	# 	| docker-compose -f - up


#TODO: deprecate compose-authx-down
#>>>
# close all authentication and authorization services

#<<<
compose-authx-down:
	# closes primary authn and authx components
	docker-compose -f ${PWD}/lib/compose/docker-compose.yml -f $(DIR)/lib/authentication/docker-compose.yml down
	docker-compose -f ${PWD}/lib/compose/docker-compose.yml -f $(DIR)/lib/authorization/docker-compose.yml down
	# - remove intermittent docker images
	# -- authentication
	docker rmi compose_keycloak:latest --force
	docker rmi compose_tyk:latest --force
	# -- authorization
	#docker rmi compose_vault:latest --force
	docker rmi compose_candig-server-authorization:latest --force

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
	docker volume rm keycloak-data
	# clean tyk
	docker volume rm tyk-data
	docker volume rm tyk-redis-data
	# clean vault
	docker volume rm vault-data


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
	if [[ ${KEYCLOAK_SERVICE_PUBLIC_URL} == *":443"* ]]; then \
		echo "option 1"; \
		$(eval TEMP_KEYCLOAK_SERVICE_PUBLIC_URL=$(shell echo ${KEYCLOAK_SERVICE_PUBLIC_URL} | sed -e 's/\(:443\)\$//g')) \
	elif [[ ${KEYCLOAK_SERVICE_PUBLIC_URL} == *":80"* ]]; then \
		echo "option 2"; \
		$(eval TEMP_KEYCLOAK_SERVICE_PUBLIC_URL=$(shell echo ${KEYCLOAK_SERVICE_PUBLIC_URL} | sed -e 's/\(:80\)\$//g')) \
	else \
		echo "option 3"; \
		$(eval TEMP_KEYCLOAK_SERVICE_PUBLIC_URL=$(shell echo ${KEYCLOAK_SERVICE_PUBLIC_URL})) \
	fi


	# inject dynamic variables in a "Makefile-ish" way
	# by chaining these calls "all in one line" so that
	# variables properly get exported from each sub script
	# and propogate to the next ones
	export KEYCLOAK_CLIENT_ID_64=$(KEYCLOAK_CLIENT_ID_64); \
	export TEMP_KEYCLOAK_SERVICE_PUBLIC_URL=$(TEMP_KEYCLOAK_SERVICE_PUBLIC_URL); \
	\
	echo ; \
	echo "Setting up Keycloak;" ; \
	source ${PWD}/etc/setup/scripts/subtasks/keycloak_setup.sh; \
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
	docker-compose -f ${DIR}/lib/compose/docker-compose.yml -f $(DIR)/lib/candig-server/docker-compose.yml up -d candig-server 2>&1


#>>>
# run authentication and authorization
# tests with both chrome and firefox front-ends

#<<<
#TODO: fix broken tests
#test-authx-prototype:
	#$(DIR)/etc/tests/integration/authx/run_tests.sh 20 chrome True
	#$(DIR)/etc/tests/integration/authx/run_tests.sh 20 firefox True


#>>>
# deploy/test individual modules using docker-compose
# $module is the name of the sub-folder in lib/
# make compose-$module

#<<<
compose-%:
	echo "    started compose-$*" >> $(LOGFILE)
	cat $(DIR)/lib/compose/docker-compose.yml $(DIR)/lib/logging/$(DOCKER_LOG_DRIVER)/docker-compose.yml \
		$(DIR)/lib/$*/docker-compose.yml \
		| docker-compose -f - up -d
	echo "    finished compose-$*" >> $(LOGFILE)

#>>>
# create docker bridge networks
# make docker-networks

#<<<
.PHONY: docker-networks
docker-networks:
	docker network create --driver bridge --subnet=$(DOCKER_BRIDGE_IP) --attachable bridge-net
	docker network create --driver bridge --subnet=$(DOCKER_GWBRIDGE_IP) --attachable \
		-o com.docker.network.bridge.enable_icc=false \
		-o com.docker.network.bridge.name=docker_gwbridge \
		-o com.docker.network.bridge.enable_ip_masquerade=true \
		docker_gwbridge

#>>>
# pull images from $DOCKER_REGISTRY
# make docker-pull

#<<<
.PHONY: docker-pull
docker-pull:
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) pull-$(MODULE);)
	$(foreach MODULE, $(TOIL_MODULES), docker pull $(DOCKER_REGISTRY)/$(MODULE):latest;)

#>>>
# push docker images to $DOCKER_REGISTRY
# make docker-push

#<<<
.PHONY: docker-push
docker-push:
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) push-$(MODULE);)

#>>>
# create secrets for CanDIG services
# make docker-secrets

#<<<
.PHONY: docker-secrets
docker-secrets: minio-secrets
	@echo admin > $(DIR)/tmp/secrets/portainer-user
	$(MAKE) secret-portainer-secret
	$(MAKE) secret-metadata-app-secret
	@echo admin > $(DIR)/tmp/secrets/metadata-db-user
	$(MAKE) secret-metadata-db-secret
	@echo ${KEYCLOAK_ADMIN_USER} > $(DIR)/tmp/secrets/keycloak-admin-user
	#TODO: use random generated pw instead of env-var
	@echo ${KEYCLOAK_ADMIN_PW} > $(DIR)/tmp/secrets/keycloak-admin-password
	#$(MAKE) secret-keycloak-admin-password

#>>>
# create persistant volumes for docker containers
# make docker-volumes

#<<<
.PHONY: docker-volumes
docker-volumes:
	docker volume create consul-data
	docker volume create datasets-data
	docker volume create grafana-data
	docker volume create jupyter-data
	docker volume create mc-config
	docker volume create minio-config
	docker volume create minio-data $(MINIO_VOLUME_OPT)
	docker volume create portainer-data
	docker volume create prometheus-data
	docker volume create toil-jobstore
	docker volume create traefik-data
	docker volume create keycloak-data
	docker volume create tyk-data
	docker volume create tyk-redis-data
	docker volume create vault-data

#>>>
# (re)build service image for all modules
# add BUILD_OPTS='--no-cache' to ignore cached builds
# BUILD_OPTS='--no-cache' make build-$module
# make images

#<<<
.PHONY: images
images: #toil-docker
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) build-$(MODULE);)

#>>>
# initialize conda environment
# make init-conda

#<<<
.PHONY: init-conda
init-conda:
	echo "    started init-conda" >> $(LOGFILE)
	$(CONDA) create -y -n $(VENV_NAME) python=$(VENV_PYTHON) pip=$(VENV_PIP)
	@echo "Load local conda: source $(DIR)/bin/miniconda3/etc/profile.d/conda.sh"
	@echo "Activate conda env: conda activate $(VENV_NAME)"
	@echo "Install requirements: pip install -U -r $(DIR)/etc/venv/requirements.txt"
	echo "    finished init-conda" >> $(LOGFILE)

#>>>
# initialize docker and create required docker networks, volumes, certs, secrets, and conda env
# make init-docker

#<<<
.PHONY: init-docker
init-docker: docker-networks docker-volumes ssl-cert docker-secrets

#>>>
# initialize kubernetes environment
# make init-kubernetes

#<<<
.PHONY: init-kubernetes
init-kubernetes:ssl-cert docker-secrets docker-pull
	$(DIR)/bin/kubectl create namespace $(DOCKER_NAMESPACE)

#>>>
# initialize docker-swarm environment and create swarm networks, configs, and secrets
# make init-swarm

#<<<
.PHONY: init-swarm
init-swarm: swarm-init swarm-networks swarm-configs swarm-secrets

#>>>
# deploy/test all modules in $CANDIG_MODULES using Kubernetes
# make kubernetes

#<<<
.PHONY: kubernetes
kubernetes:
	$(DIR)/bin/kompose --file $(DIR)/lib/kubernetes/docker-compose.yml \
		$(foreach MODULE, $(CANDIG_MODULES), --file $(DIR)/lib/$(MODULE)/docker-compose.yml) \
		up

#>>>
# deploys individual module using kompose
# $module is the name of the sub-folder in lib
# make kube-$module

#<<<
kube-%:
	$(DIR)/bin/kompose --file $(DIR)/lib/kubernetes/docker-compose.yml \
		--file $(DIR)/lib/$*/docker-compose.yml up

#>>>
# create docker-machine instance(s) for Docker Compose/Swarm development
# NOTE: only virtualbox is supported at this time
# NOTE: use MINIKUBE_* to configure vm options
# $vm_name must be a unique name for the docker-machine instance (e.g. make machine-manager)
# make machine-$vm_name

#<<<
machine-%:
	$(DIR)/bin/docker-machine create --driver "$(MINIKUBE_DRIVER)" \
  		--virtualbox-cpu-count "$(MINIKUBE_CPUS)" --virtualbox-memory "$(MINIKUBE_MEM)" \
		--virtualbox-disk-size "$(MINIKUBE_DISK)" --virtualbox-hostonly-cidr "192.168.56.1/24" \
		--virtualbox-hostonly-nicpromisc "deny" --virtualbox-hostonly-nictype "82540EM" \
		$*

#>>>
# create minikube environment for (kubernetes) integration testing
# make minikube

#<<<
.PHONY: minikube
minikube:
	$(DIR)/bin/minikube start --container-runtime $(MINIKUBE_CRI) \
		--cpus $(MINIKUBE_CPUS) --memory $(MINIKUBE_MEM) --disk-size $(MINIKUBE_DISK) \
		--network-plugin cni --cni $(MINIKUBE_CNI) --driver $(MINIKUBE_DRIVER) \
		--dns-domain $(CANDIG_DOMAIN) --nodes $(MINIKUBE_NODES)

#>>>
# generate secrets for minio server/client
# make minio-secrets

#<<<
minio-secrets:
	@echo admin > $(DIR)/tmp/secrets/minio-access-key
	$(MAKE) secret-minio-secret-key
	@echo '[default]' > $(DIR)/tmp/secrets/aws-credentials
	@echo "aws_access_key_id=`cat tmp/secrets/minio-access-key`" >> $(DIR)/tmp/secrets/aws-credentials
	@echo "aws_secret_access_key=`cat tmp/secrets/minio-secret-key`" >> $(DIR)/tmp/secrets/aws-credentials

#>>>
# pull docker image to $DOCKER_REGISTRY
# $module is the name of the sub-folder in lib/
# make pull-$module

#<<<
pull-%:
		cat $(DIR)/lib/compose/docker-compose.yml $(DIR)/lib/logging/$(DOCKER_LOG_DRIVER)/docker-compose.yml \
			$(DIR)/lib/$*/docker-compose.yml \
			| docker-compose -f - pull

#>>>
# push docker image to $DOCKER_REGISTRY
# $module is the name of the sub-folder in lib/
# make push-$module

#<<<
push-%:
		cat $(DIR)/lib/compose/docker-compose.yml $(DIR)/lib/logging/$(DOCKER_LOG_DRIVER)/docker-compose.yml \
			$(DIR)/lib/$*/docker-compose.yml \
			| docker-compose -f - push

#>>>
# create a random secret and add it to tmp/secrets/$secret_name
# make secret-$secret_name

#<<<
secret-%:
	@dd if=/dev/urandom bs=1 count=16 2>/dev/null \
		| base64 | rev | cut -b 2- | rev | tr -d '\n\r' > $(DIR)/tmp/secrets/$*

#>>>
# generate root-ca and site ssl certs using openssl
# make ssl-cert

#<<<
ssl-cert:
	openssl genrsa -out $(DIR)/tmp/ssl/selfsigned-root-ca.key 4096
	openssl req -new -key $(DIR)/tmp/ssl/selfsigned-root-ca.key \
		-out $(DIR)/tmp/ssl/selfsigned-root-ca.csr -sha256 \
		-subj '/C=CA/ST=ON/L=Toronto/O=CanDIG/CN=CanDIG Self-Signed CA'
	openssl x509 -req -days 3650 -in $(DIR)/tmp/ssl/selfsigned-root-ca.csr \
		-signkey $(DIR)/tmp/ssl/selfsigned-root-ca.key -sha256 \
		-out $(DIR)/tmp/ssl/selfsigned-root-ca.crt \
		-extfile $(DIR)/etc/ssl/root-ca.cnf -extensions root_ca
	openssl genrsa -out $(DIR)/tmp/ssl/selfsigned-site.key 4096
	openssl req -new -key $(DIR)/tmp/ssl/selfsigned-site.key \
		-out $(DIR)/tmp/ssl/selfsigned-site.csr -sha256 \
		-subj '/C=CA/ST=ON/L=Toronto/O=CanDIG/CN=CanDIG Self-Signed Cert'
	openssl x509 -req -days 750 -in $(DIR)/tmp/ssl/selfsigned-site.csr -sha256 \
		-CA $(DIR)/tmp/ssl/selfsigned-root-ca.crt \
		-CAkey $(DIR)/tmp/ssl/selfsigned-root-ca.key \
		-CAcreateserial -out $(DIR)/tmp/ssl/selfsigned-site.crt \
		-extfile $(DIR)/etc/ssl/site.cnf -extensions server

#>>>
# deploy/test all modules in $CANDIG_MODULES using docker stack
# make stack

#<<<
.PHONY: stack
stack:
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) stack-$(MODULE);)

#>>>
# deploy/test indivudual modules using docker stack
# $module is the name of the sub-folder in lib/
# make stack-$module

#<<<
stack-%:
	cat $(DIR)/lib/swarm/docker-compose.yml \
		$(DIR)/lib/logging/$(DOCKER_LOG_DRIVER)/docker-compose.yml \
		$(DIR)/lib/$*/docker-compose.yml > $(DIR)/tmp/data/docker-compose.yml
	docker stack deploy --compose-file $(DIR)/tmp/data/docker-compose.yml $(DOCKER_NAMESPACE)

#>>>
# initialize primary docker-swarm master node
# make swarm-init

#>>>
# create docker configs for CanDIG services (swarm only)
# configs are distributed to all swarm nodes
# make swarm-configs

#<<<
.PHONY: swarm-configs
swarm-configs:
	docker config create chord-metadata-settings $(DIR)/lib/chord-metadata/settings.py
	docker config create wes-dependency-resolver $(DIR)/etc/yml/$(WES_DEPENDENCY_RESOLVER).yml

#<<<
.PHONY: swarm-init
swarm-init:
	docker swarm init --advertise-addr $(SWARM_ADVERTISE_IP) --listen-addr $(SWARM_LISTEN_IP)
	@docker swarm join-token manager -q > $(DIR)/tmp/secrets/swarm-manager-token
	@docker swarm join-token worker -q > $(DIR)/tmp/secrets/swarm-worker-token

#>>>
# join a docker swarm cluster using manager/worker token
# make swarm-join

#<<<
.PHONY: swarm-join
swarm-join:
	@docker swarm join --advertise-addr $(SWARM_ADVERTISE_IP) --listen-addr $(SWARM_LISTEN_IP) \
		--token `cat $(DIR)/tmp/secrets/swarm-$(SWARM_MODE)-token` $(SWARM_MANAGER_IP)

.PHONY: swarm-networks
swarm-networks:
	docker network create --driver overlay --opt encrypted=true traefik-net
	docker network create --driver overlay --internal --opt encrypted=true agent-net

#>>>
# create docker swarm compatbile secrets
# make swarm-secrets

#<<<
.PHONY: swarm-secrets
swarm-secrets:
	docker secret create minio-access-key $(DIR)/tmp/secrets/minio-access-key
	docker secret create minio-secret-key $(DIR)/tmp/secrets/minio-secret-key
	docker secret create aws-credentials $(DIR)/tmp/secrets/aws-credentials
	docker secret create portainer-user $(DIR)/tmp/secrets/portainer-user
	docker secret create portainer-secret $(DIR)/tmp/secrets/portainer-secret
	docker secret create traefik-ssl-key $(DIR)/tmp/ssl/$(TRAEFIK_SSL_CERT).key
	docker secret create traefik-ssl-crt $(DIR)/tmp/ssl/$(TRAEFIK_SSL_CERT).crt
	docker secret create metadata-app-secret $(DIR)/tmp/secrets/metadata-app-secret
	docker secret create metadata-db-user $(DIR)/tmp/secrets/metadata-db-user
	docker secret create metadata-db-secret $(DIR)/tmp/secrets/metadata-db-secret
	docker secret create keycloak-admin-user $(DIR)/tmp/secrets/keycloak-admin-user
	docker secret create keycloak-admin-password $(DIR)/tmp/secrets/keycloak-admin-password

#>>>
# create toil images using upstream CanDIG Toil repo
# make toil-docker

#<<<
.PHONY: toil-docker
toil-docker:
	echo "    started toil-docker" >> $(LOGFILE)
	VIRTUAL_ENV=1 DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 TOIL_DOCKER_REGISTRY=$(DOCKER_REGISTRY) $(MAKE) -C $(DIR)/lib/toil/toil-docker docker
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION)-$(TOIL_BUILD_HASH) \
		$(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION);)
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION) \
		$(DOCKER_REGISTRY)/$(MODULE):latest;)
	$(foreach MODULE, $(TOIL_MODULES), docker push $(DOCKER_REGISTRY)/$(MODULE):latest;)
	echo "    finished toil-docker" >> $(LOGFILE)

#>>>
# deploys all modules using Tox
# make tox

#<<<
.PHONY: tox
tox:
	dotenv -f .env run tox

#>>>
# deploys individual module using tox
# $module is the name of the sub-folder in lib/
# make tox-$module

#<<<
tox-%:
	dotenv -f .env run tox -e $*

# test print global variables
print-%:
	@echo '$*=$($*)'

#>>>
# view available options
# make help

#<<<
# Find sections of docstrings #>>> #<<< and print
.PHONY: help
help:
	@sed -n -e '/^#>>>/,/^#<<</ { /^#>>>/d; /^#<<</d; p; }' Makefile \
		| sed 's/# make/make/g'
