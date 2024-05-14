#!make

# import global variables
env ?= .env

include $(env)
export $(shell sed 's/=.*//' $(env))

SHELL = bash
#>>>
# option A : set CONDA_INSTALL to bin to install conda within the candigv2 repo
#  and then use make bin-conda and make init-conda
# option B: set CONDA_INSTALL to the location of an existing miniconda3 installation
#  and then use make mkdir and make init-conda (no bin-conda, which will blow up an existing conda)
# <<<

CONDA = $(CONDA_INSTALL)/bin/conda
CONDA_ENV_SETTINGS = $(CONDA_INSTALL)/etc/profile.d/conda.sh


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
	mkdir -p bin
	mkdir -p $(CONDA_INSTALL)
	mkdir -p tmp/secrets


#>>>
# download all package binaries
# make bin-all

#<<<
.PHONY: bin-all
bin-all: bin-conda


#>>>
# download miniconda package
# make bin-conda

#<<<
bin-conda: mkdir
ifndef CONDA_INSTALL
	echo "ERROR: Conda install location not specified. Do you have a .env?"
	exit 1
endif
	@printf "\nOutput of bin-conda:\n" | tee -a $(LOGFILE)
ifeq ($(VENV_OS), linux)
	curl -Lo bin/miniforge_install.sh \
		https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
	bash bin/miniforge_install.sh -f -b -u -p $(CONDA_INSTALL)
	# init is needed to create bash aliases for conda but it won't work
	# until you source the script that ships with conda
	source $(CONDA_ENV_SETTINGS) && $(CONDA) init
endif
ifeq ($(VENV_OS), darwin)
	curl -Lo bin/miniforge_install.sh \
		https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh
	bash bin/miniforge_install.sh -f -b -u -p $(CONDA_INSTALL)
	# init is needed to create bash aliases for conda but it won't work
	# until you source the script that ships with conda
	source $(CONDA_ENV_SETTINGS) && $(CONDA) init
endif
ifeq ($(VENV_OS), arm64mac)
	curl -Lo bin/miniforge_install.sh \
		https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
	bash bin/miniforge_install.sh -f -b -u -p $(CONDA_INSTALL)
	# init is needed to create bash aliases for conda but it won't work
	# until you source the script that ships with conda
	source $(CONDA_ENV_SETTINGS) && $(CONDA) init zsh
endif
	echo `$(CONDA) config --show-sources`

#>>>
# make build-all -P

#<<<
.PHONY: build-all
build-all: mkdir
	@printf "Build started at `date '+%D %T'`.\n\n" >> $(LOGFILE)
	./pre-build-check.sh $(ARGS)

# Setup the entire stack
	$(MAKE) init-docker
	pip install --upgrade setuptools
	pip install -U -r etc/venv/requirements.txt
	touch tmp/containers.txt
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) build-$(MODULE); $(MAKE) compose-$(MODULE);)
	./post_build.sh

.PHONY: install-all
install-all:
	$(MAKE) bin-conda
	$(MAKE) init-conda
	$(MAKE) build-all


#>>>
# (re)build service image for all modules
# add BUILD_OPTS='--no-cache' to ignore cached builds
# BUILD_OPTS='--no-cache' make build-$module
# make images

#<<<
.PHONY: build-images
build-images: #toil-docker
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) build-$(MODULE);)


#>>>
# (re)build service image and deploy/test using docker-compose
# $module is the name of the sub-folder in lib/
# add BUILD_OPTS='--no-cache' to ignore cached builds
# BUILD_OPTS='--no-cache' make build-$module
# make build-$module

#<<<
build-%:
	@printf "\nOutput of build-$*: \n" | tee -a $(LOGFILE)
	source setup_hosts.sh
	if [ -f lib/$*/$*_preflight.sh ]; then \
	source lib/$*/$*_preflight.sh 2>&1 | tee -a $(LOGFILE); \
	fi
	export SERVICE_NAME=$*; \
	DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 \
	docker compose -f lib/candigv2/docker-compose.yml -f lib/$*/docker-compose.yml build $(BUILD_OPTS) 2>&1 | tee -a $(LOGFILE)
	echo "    finished build-$*" >> $(LOGFILE)


#>>>
# clean target: remove container, volumes, tempfiles
# make clean-%

#<<<
clean-%:
	echo "    started clean-$*"
	source setup_hosts.sh
	export SERVICE_NAME=$*; \
	docker compose -f lib/candigv2/docker-compose.yml -f lib/$*/docker-compose.yml down || true
	-docker volume rm `docker volume ls --filter name=$* -q`
	-docker image rm `docker image ls --format "{{.Repository}}:{{.Tag}}" | grep $*`
	-rm -Rf lib/$*/tmp
	-rm -f tmp/$*/*


#>>>
# run all cleanup functions
# WARNING: these are destructive steps, read through instructions before using
# make clean-all

#<<<
.PHONY: clean-all
clean-all: clean-logs clean-compose clean-containers clean-secrets \
	clean-volumes clean-images# clean-bin
	rm -f tmp/containers.txt


#>>>
# close all authentication and authorization services
# make clean-authx

#<<<
.PHONY: clean-authx
clean-authx:
	mv tmp/vault/service_stores.txt tmp/vault_service_stores.txt
	$(foreach MODULE, $(CANDIG_AUTH_MODULES), $(MAKE) clean-$(MODULE);)
	-mkdir tmp/vault
	mv tmp/vault_service_stores.txt tmp/vault/service_stores.txt


# Empties error and progress logs
.PHONY: clean-logs
clean-logs:
	> $(LOGFILE)

#>>>
# clear downloaded binaries
# removes $PWD/bin/
# make clean-bin

#<<<
.PHONY: clean-bin
clean-bin:
	rm -f bin/*


#>>>
# stops and removes docker-compose instances
# make clean-compose

#<<<
.PHONY: clean-compose
clean-compose:
	source setup_hosts.sh; \
	$(eval CANDIG_MODULES := $(filter-out logging,$(CANDIG_MODULES))) \
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) clean-$(MODULE);) \
	$(MAKE) clean-logging;


#>>>
# deactivate and remove conda env $VENV_NAME
# make clean-conda


#<<<
.PHONY: clean-conda
clean-conda:
	$(CONDA) deactivate
	$(CONDA) env remove -n $(VENV_NAME)


#>>>
# remove all stopped containers - does not stop any running containers.
# make clean-containers

#<<<
.PHONY: clean-containers
clean-containers:
	docker container prune -f --filter "label=candigv2"


#>>>
# clear all images (including base images)
# make clean-images

#<<<
.PHONY: clean-images
clean-images:
	docker image prune -a -f


#>>>
# clear swarm secrets and remove secret files
# make clean-secrets

#<<<
.PHONY: clean-secrets
clean-secrets:
	-docker secret rm `docker secret ls -q --filter label=candigv2`
	rm -f tmp/secrets/*


#>>>
# remove all persistent volumes and local data
# make clean-volumes

#<<<
.PHONY: clean-volumes
clean-volumes:
	-docker volume rm `docker volume ls -q --filter label=candigv2`
	-docker volume rm `docker volume ls -q --filter dangling=true`


#>>>
# deploy/test all modules in $CANDIG_MODULES using docker-compose
# make compose

#<<<
.PHONY: compose
compose:
	source setup_hosts.sh; \
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) compose-$(MODULE);)


#>>>
# deploy/test individual modules using docker-compose
# $module is the name of the sub-folder in lib/
# make compose-$module

containers=$(shell cat lib/$*/docker-compose.yml | yq -ojson '.services' | jq  'keys' | jq -r @sh)
found=$(shell grep -ch $(containers) tmp/containers.txt)
#<<<
compose-%:
	@printf "\nOutput of compose-$*: \n" | tee -a $(LOGFILE)
	@source setup_hosts.sh; \
	python settings.py; source env.sh; \
	if [ $* != "keycloak" ]; then \
	if [ $* != "logging" ]; then \
	echo "getting site admin token"; \
	python site_admin_token.py ; \
	fi \
	fi; \
	export SERVICE_NAME=$*; \
	docker compose -f lib/candigv2/docker-compose.yml -f lib/$*/docker-compose.yml --compatibility up -d 2>&1 | tee -a $(LOGFILE)
	if [ $(found) -eq 0 ]; then \
	echo $(containers) >> tmp/containers.txt; \
	fi
	if [ -f lib/$*/$*_setup.sh ]; then \
	source lib/$*/$*_setup.sh 2>&1 | tee -a $(LOGFILE); \
	fi
	-chmod -R $(DIR_PERMISSIONS) tmp/ 2>/dev/null || true
	-chmod -R 777 tmp/logs 2>/dev/null || true

#>>>
# Combines the make clean/build/compose steps (and re-creates docker volumes)
# $module is the name of the sub-folder in lib/
# make recompose-$module

#<<<
recompose-%:
	$(MAKE) clean-$*
	$(MAKE) docker-volumes
	$(MAKE) build-$*
	$(MAKE) compose-$*

#>>>
# Combines the make clean/build/compose steps (and re-creates docker volumes)
# $module is the name of the sub-folder in lib/
# make recompose-$module

#<<<
recompose-%:
	$(MAKE) clean-$*
	$(MAKE) docker-volumes
	$(MAKE) build-$*
	$(MAKE) compose-$*

#>>>
# take down individual modules using docker-compose
# $module is the name of the sub-folder in lib/
# make down-$module

#<<<
down-%:
	@printf "\nOutput of down-$*: \n" | tee -a $(LOGFILE)
	source setup_hosts.sh; \
	export SERVICE_NAME=$*; \
	docker compose -f lib/candigv2/docker-compose.yml -f lib/$*/docker-compose.yml --compatibility down 2>&1
	echo "    finished down-$*" >> $(LOGFILE)


#>>>
# pull images from $DOCKER_REGISTRY
# make docker-pull

#<<<
.PHONY: docker-pull
docker-pull:
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) pull-$(MODULE);)
#$(foreach MODULE, $(TOIL_MODULES), docker pull $(DOCKER_REGISTRY)/$(MODULE):latest;)


#>>>
# push docker images to $DOCKER_REGISTRY
# make docker-push

#<<<
.PHONY: docker-push
docker-push:
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) push-$(MODULE);)
#$(foreach MODULE, $(TOIL_MODULES), docker push $(DOCKER_REGISTRY)/$(MODULE):latest;)


#>>>
# create secrets for CanDIG services
# make docker-secrets

#<<<
.PHONY: docker-secrets
docker-secrets: mkdir authx-secrets data-secrets


data-secrets: mkdir
	@echo "making data secrets"
	$(MAKE) secret-postgres-db-secret
	$(MAKE) secret-redis-secret-key


authx-secrets: mkdir
	@echo "making authx secrets"
	$(MAKE) secret-keycloak-admin-password

	$(MAKE) secret-keycloak-test-site-admin-password
	$(MAKE) secret-keycloak-test-user-password
	$(MAKE) secret-keycloak-test-user2-password

	$(MAKE) secret-tyk-secret-key
	$(MAKE) secret-tyk-analytics-admin-key


minio-secrets: mkdir
	@echo "making minio secrets"
	@echo $(DEFAULT_ADMIN_USER) > lib/minio/access-key
	$(MAKE) secret-minio-secret-key
	mv tmp/secrets/minio-secret-key lib/minio/secret-key
	@echo '[default]' > lib/minio/aws-credentials
	@echo "aws_access_key_id=`cat lib/minio/access-key`" >> lib/minio/aws-credentials
	@echo "aws_secret_access_key=`cat lib/minio/secret-key`" >> lib/minio/aws-credentials


#>>>
# create persistent volumes for docker containers
# make docker-volumes

#<<<
.PHONY: docker-volumes
docker-volumes:
	docker volume create grafana-data --label candigv2=volume
	docker volume create jupyter-data --label candigv2=volume
	docker volume create prometheus-data --label candigv2=volume
	docker volume create toil-jobstore --label candigv2=volume
	docker volume create keycloak-data --label candigv2=volume
	docker volume create tyk-data --label candigv2=volume
	docker volume create redis-data --label candigv2=volume
	docker volume create vault-data --label candigv2=volume
	docker volume create opa-data --label candigv2=volume
	docker volume create htsget-data --label candigv2=volume
	docker volume create postgres-data --label candigv2=volume
	docker volume create query-data --label candigv2=volume


#>>>
# authx, common settings
# make init-authx

#<<<
.PHONY: init-authx
init-authx: mkdir
	$(MAKE) docker-volumes
	$(MAKE) authx-secrets
	$(foreach MODULE, $(CANDIG_AUTH_MODULES), $(MAKE) build-$(MODULE); $(MAKE) compose-$(MODULE); python settings.py;)


#>>>
# create a minio container (that won't be removed as part of clean-all)
# make init-minio

#<<<
init-minio: minio-secrets
	docker volume create minio-config
	docker volume create minio-data $(MINIO_VOLUME_OPT)
	docker compose -f lib/candigv2/docker-compose.yml -f lib/minio/docker-compose.yml --compatibility up -d 2>&1 | tee -a $(LOGFILE)


#>>>
# initialize conda environment
# make init-conda

#<<<
.PHONY: init-conda
init-conda:
	@printf "\nOutput of init-conda: \n" | tee -a $(LOGFILE)
	# source conda's script to be safe, so the conda command is found
	source $(CONDA_ENV_SETTINGS) \
		&& $(CONDA) create -y -n $(VENV_NAME) python=$(VENV_PYTHON) pip=$(VENV_PIP)

	source $(CONDA_ENV_SETTINGS) \
		&& conda activate $(VENV_NAME) \
		&& pip install --upgrade setuptools \
		&& pip install -U -r etc/venv/requirements.txt

#@echo "Load local conda: source bin/miniconda3/etc/profile.d/conda.sh"
#@echo "Activate conda env: conda activate $(VENV_NAME)"
#@echo "Install requirements: pip install -U -r etc/venv/requirements.txt"


#>>>
# initialize docker and create required docker networks, volumes, certs, secrets, and conda env
# make init-docker

#<<<
.PHONY: init-docker
init-docker: docker-volumes docker-secrets


#>>>
# pull docker image to $DOCKER_REGISTRY
# $module is the name of the sub-folder in lib/
# make pull-$module

#<<<
pull-%:
		docker compose -f lib/candigv2/docker-compose.yml -f lib/$*/docker-compose.yml pull


#>>>
# push docker image to $DOCKER_REGISTRY
# $module is the name of the sub-folder in lib/
# make push-$module

#<<<
push-%:
		docker compose -f lib/candigv2/docker-compose.yml -f lib/$*/docker-compose.yml push


#>>>
# create a random secret and add it to tmp/secrets/$secret_name
# make secret-$secret_name

#<<<
secret-%:
	@dd if=/dev/urandom bs=1 count=16 2>/dev/null \
		| base64 | tr -d '\n\r+' | sed s/[^A-Za-z0-9]//g > tmp/secrets/$*


#>>>
# create toil images using upstream CanDIG Toil repo
# make toil-docker

#<<<
.PHONY: toil-docker
toil-docker:
	@printf "\nOutput of toil-docker: \n" | tee -a $(LOGFILE)
	VIRTUAL_ENV=1 DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 TOIL_DOCKER_REGISTRY=$(DOCKER_REGISTRY) \
	$(MAKE) -C lib/toil/toil-docker docker
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION)-$(TOIL_BUILD_HASH) \
		$(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION);)
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION) \
		$(DOCKER_REGISTRY)/$(MODULE):latest;)
	$(foreach MODULE, $(TOIL_MODULES), docker push $(DOCKER_REGISTRY)/$(MODULE):latest;)


#>>>
# view available options
# make help

#<<<
.PHONY: help
help:
# Find sections of docstrings #>>> #<<< and print
	@sed -n -e '/^#>>>/,/^#<<</ { /^#>>>/d; /^#<<</d; p; }' Makefile \
		| sed 's/# make/make/g'


#>>>
# test print global variables
# make print-ENV_VARIABLE

#<<<
print-%:
	@echo '$*=$($*)'

#>>>
# run integration tests

#<<<
.PHONY: test-integration
test-integration:
	mkdir -p tmp/test
	python ./settings.py
ifeq ($(KEEP_TEST_DATA),true)
	source ./env.sh; pytest -v --color=yes ./etc/tests/integration -k 'not test_clean_up' $(ARGS) --report-log=./tmp/test/test-integration_$(shell date +"%Y-%m-%d_%Hh%Mm%Ss").jsonl
else
	source ./env.sh; pytest -v --color=yes ./etc/tests/integration $(ARGS) --report-log=./tmp/test/test-integration_$(shell date +"%Y-%m-%d_%Hh%Mm%Ss").jsonl
endif

# Run a single test by using its name and print out results whether failing or passing
# note some tests are dependent on others so doesn't always work as expected
# Helpful when debugging issues with a specific test
.PHONY: test-integration-%
test-integration-%:
	mkdir -p tmp/test
	python ./settings.py; source ./env.sh; pytest -v --color=yes ./etc/tests -s -rP -k '$*' --report-log=./tmp/test/test-integration_$(shell date +"%Y-%m-%d_%Hh%Mm%Ss").jsonl

#>>>
# run local federation setup tests
# these aren't really federation tests, but instead setup datasets for another site to test their federation

#<<<
.PHONY: test-local-federation
test-local-federation:
	mkdir -p tmp/test
	python ./settings.py
	source ./env.sh; pytest -v --color=yes ./etc/tests/federation -k "all or local" $(ARGS) --report-log=./tmp/test/test-federation_$(shell date +"%Y-%m-%d_%Hh%Mm%Ss").jsonl

#>>>
# run querying federation setup tests
# these require other, federated sites to have run test-local-federation

#<<<
.PHONY: test-querying-federation
test-querying-federation:
	mkdir -p tmp/test
	python ./settings.py
	source ./env.sh; pytest -v --color=yes ./etc/tests/federation -k "all or querying_site" $(ARGS) --report-log=./tmp/test/test-federation_$(shell date +"%Y-%m-%d_%Hh%Mm%Ss").jsonl

# stop all docker containers
.PHONY: stop-all
stop-all:
	CONTAINERS="$(shell cat tmp/containers.txt | sed 's/ /\n/g' | sed 's/^\(.*\)$$/candigv2_\1_1/g' | sed -n '1!G;h;$$p')"; for CONTAINER in $$CONTAINERS; do docker stop $$CONTAINER; done

# start all docker containers
.PHONY: start-all
start-all:
	CONTAINERS="$(shell cat tmp/containers.txt | sed 's/ /\n/g' | sed 's/^\(.*\)$$/candigv2_\1_1/g')"; for CONTAINER in $$CONTAINERS; do docker start $$CONTAINER; sleep 2; done

#>>>
# rebuild the entire stack without touching the data containers, defined in .env
### $(MAKE) clean-all CANDIG_MODULES="$(CANDIG_MODULES)"
#<<<

.PHONY: rebuild-keep-data
rebuild-keep-data:
	# Remove the data modules from CANDIG_MODULES
	$(eval REBUILD_CANDIG_MODULES := $(filter-out $(CANDIG_DATA_MODULES),$(CANDIG_MODULES)))
	# Clean only the remaining modules
	$(foreach MODULE, $(REBUILD_CANDIG_MODULES), $(MAKE) clean-$(MODULE);)
	# Prune unused Docker resources
	docker system prune -af
	# Start build-all
	./pre-build-check.sh $(ARGS)
	$(MAKE) init-docker
	# Rebuild deleted modules
	$(foreach MODULE, $(REBUILD_CANDIG_MODULES), $(MAKE) build-$(MODULE); $(MAKE) compose-$(MODULE);)
	# Run post-build tasks
	./post_build.sh

# wrapper for make_backup.sh to make sure we're running it from the right directory
backup-vault:
	@bash lib/vault/make_backup.sh
	-$(MAKE) compose-vault
	-$(MAKE) compose-opa


# if there is a restore file available, restore it and then run compose-opa again
restore-vault:
	ls lib/vault/restore.tar.gz
	-$(MAKE) clean-vault
	-$(MAKE) secret-vault-approle-token
	-$(MAKE) docker-volumes
	-$(MAKE) build-vault
	-$(MAKE) compose-vault
	-$(MAKE) compose-opa
