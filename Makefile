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

LOGFILE = tmp/progress.txt

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
	mkdir -p tmp/{configs,data,secrets}
	mkdir -p tmp/{keycloak,tyk,vault}


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
	echo "    started bin-conda" >> $(LOGFILE)
ifeq ($(VENV_OS), linux)
	curl -Lo bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
	bash bin/miniconda_install.sh -f -b -u -p $(CONDA_INSTALL)
	# init is needed to create bash aliases for conda but it won't work
	# until you source the script that ships with conda
	source $(CONDA_ENV_SETTINGS) && $(CONDA) init
	echo "    finished bin-conda" >> $(LOGFILE)
endif
ifeq ($(VENV_OS), darwin)
	curl -Lo bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
	bash bin/miniconda_install.sh -f -b -u -p $(CONDA_INSTALL)
	# init is needed to create bash aliases for conda but it won't work
	# until you source the script that ships with conda
	source $(CONDA_ENV_SETTINGS) && $(CONDA) init
	echo "    finished bin-conda" >> $(LOGFILE)
endif
ifeq ($(VENV_OS), arm64mac)
	curl -Lo bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
	bash bin/miniconda_install.sh -f -b -u -p $(CONDA_INSTALL)
	# init is needed to create bash aliases for conda but it won't work
	# until you source the script that ships with conda
	source $(CONDA_ENV_SETTINGS) && $(CONDA) init zsh
	echo "    finished bin-conda" >> $(LOGFILE)
endif

#>>>
# make build-all -P

#<<<
.PHONY: build-all
build-all:
	printf "Build started at `date '+%D %T'`.\n\n" >> $(ERRORLOG)
	./pre-build-check.sh $(ARGS)

# Setup the entire stack
	$(MAKE) init-docker
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) build-$(MODULE); $(MAKE) compose-$(MODULE))
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
	printf "\nOutput of build-$*: \n" >> $(ERRORLOG)
	echo "    started build-$*" >> $(LOGFILE)
	source setup_hosts.sh
	if [ -f lib/$*/$*_preflight.sh ]; then \
	source lib/$*/$*_preflight.sh 2>&1 | tee -a $(ERRORLOG); \
	fi
	export SERVICE_NAME=$*; \
	DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 \
	docker compose -f lib/candigv2/docker-compose.yml -f lib/$*/docker-compose.yml build $(BUILD_OPTS) 2>&1 | tee -a $(ERRORLOG)
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
	rm -Rf lib/$*/tmp


#>>>
# run all cleanup functions
# WARNING: these are destructive steps, read through instructions before using
# make clean-all

#<<<
.PHONY: clean-all
clean-all: clean-logs clean-compose clean-containers clean-secrets \
	clean-volumes clean-images# clean-bin


#>>>
# close all authentication and authorization services
# make clean-authx

#<<<
.PHONY: clean-authx
clean-authx:
	$(foreach MODULE, $(CANDIG_AUTH_MODULES), $(MAKE) clean-$(MODULE);)


# Empties error and progress logs
.PHONY: clean-logs
clean-logs:
	> $(ERRORLOG)
	> $(LOGFILE)

#>>>
# clear downloaded binaries
# removes $PWD/bin/
# make clean-bin

#<<<
.PHONY: clean-bin
clean-bin:
	rm -rf bin


#>>>
# stops and removes docker-compose instances
# make clean-compose

#<<<
.PHONY: clean-compose
clean-compose:
	source setup_hosts.sh; \
	$(foreach MODULE, $(CANDIG_MODULES), \
		export SERVICE_NAME=$(MODULE); \
		docker compose -f lib/candigv2/docker-compose.yml -f lib/$(MODULE)/docker-compose.yml down || true;)


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
	rm -rf tmp/secrets
	rm -rf tmp/vault


#>>>
# remove all peristant volumes and local data
# make clean-volumes

#<<<
.PHONY: clean-volumes
clean-volumes:
	-docker volume rm `docker volume ls -q --filter label=candigv2`
	-docker volume rm `docker volume ls -q --filter dangling=true`
#rm -rf tmp/data


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

#<<<
compose-%:
	printf "\nOutput of compose-$*: \n" >> $(ERRORLOG)
	echo "    started compose-$*" >> $(LOGFILE)
	source setup_hosts.sh; \
	export SERVICE_NAME=$*; \
	docker compose -f lib/candigv2/docker-compose.yml -f lib/$*/docker-compose.yml --compatibility up -d 2>&1 | tee -a $(ERRORLOG)
	if [ -f lib/$*/$*_setup.sh ]; then \
	source lib/$*/$*_setup.sh 2>&1 | tee -a $(ERRORLOG); \
	fi
	echo "    finished compose-$*" >> $(LOGFILE)


#>>>
# take down individual modules using docker-compose
# $module is the name of the sub-folder in lib/
# make down-$module

#<<<
down-%:
	printf "\nOutput of down-$*: \n" >> $(ERRORLOG)
	echo "    started down-$*" >> $(LOGFILE)
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
docker-secrets: mkdir minio-secrets katsu-secrets

	@echo admin > tmp/secrets/keycloak-admin-user
	$(MAKE) secret-keycloak-admin-password

	@echo user1 > tmp/secrets/keycloak-test-user
	$(MAKE) secret-keycloak-test-user-password

	@echo user2 > tmp/secrets/keycloak-test-user2
	$(MAKE) secret-keycloak-test-user2-password

	$(MAKE) secret-tyk-secret-key
	$(MAKE) secret-tyk-node-secret-key
	$(MAKE) secret-tyk-analytics-admin-key

	$(MAKE) secret-vault-s3-token
	$(MAKE) secret-vault-approle-token

	$(MAKE) secret-opa-root-token
	$(MAKE) secret-opa-service-token



#>>>
# create persistant volumes for docker containers
# make docker-volumes

#<<<
.PHONY: docker-volumes
docker-volumes:
	docker volume create grafana-data --label candigv2=volume
	docker volume create jupyter-data --label candigv2=volume
	docker volume create minio-config --label candigv2=volume
	docker volume create minio-data $(MINIO_VOLUME_OPT) --label candigv2=volume
	docker volume create prometheus-data --label candigv2=volume
	docker volume create toil-jobstore --label candigv2=volume
	docker volume create keycloak-data --label candigv2=volume
	docker volume create tyk-data --label candigv2=volume
	docker volume create tyk-redis-data --label candigv2=volume
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
	$(foreach MODULE, $(CANDIG_AUTH_MODULES), $(MAKE) build-$(MODULE); $(MAKE) compose-$(MODULE); python settings.py;)


#>>>
# initialize conda environment
# make init-conda

#<<<
.PHONY: init-conda
init-conda:
	echo "    started init-conda" >> $(LOGFILE)
	# source conda's script to be safe, so the conda command is found
	source $(CONDA_ENV_SETTINGS) \
		&& $(CONDA) create -y -n $(VENV_NAME) python=$(VENV_PYTHON) pip=$(VENV_PIP)

	source $(CONDA_ENV_SETTINGS) \
		&& conda activate $(VENV_NAME) \
		&& pip install -U -r etc/venv/requirements.txt

#@echo "Load local conda: source bin/miniconda3/etc/profile.d/conda.sh"
#@echo "Activate conda env: conda activate $(VENV_NAME)"
#@echo "Install requirements: pip install -U -r etc/venv/requirements.txt"
	echo "    finished init-conda" >> $(LOGFILE)


#>>>
# initialize docker and create required docker networks, volumes, certs, secrets, and conda env
# make init-docker

#<<<
.PHONY: init-docker
init-docker: docker-volumes docker-secrets


#>>>
# generate secrets for minio server/client
# make minio-secrets

#<<<
minio-secrets:
	@echo admin > tmp/secrets/minio-access-key
	$(MAKE) secret-minio-secret-key
	@echo '[default]' > tmp/secrets/aws-credentials
	@echo "aws_access_key_id=`cat tmp/secrets/minio-access-key`" >> tmp/secrets/aws-credentials
	@echo "aws_secret_access_key=`cat tmp/secrets/minio-secret-key`" >> tmp/secrets/aws-credentials

#>>>
# make katsu-secret and database secret

#<<<
katsu-secrets:
	@echo admin > tmp/secrets/katsu-secret-key
	@dd if=/dev/urandom bs=1 count=50 2>/dev/null \
		| base64 | tr -d '\n\r+' | sed s/[^A-Za-z0-9]//g > tmp/secrets/katsu-secret-key

	@echo admin > tmp/secrets/metadata-db-user
	$(MAKE) secret-metadata-app-secret
	$(MAKE) secret-metadata-db-secret
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
	echo "    started toil-docker" >> $(LOGFILE)
	VIRTUAL_ENV=1 DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 TOIL_DOCKER_REGISTRY=$(DOCKER_REGISTRY) \
	$(MAKE) -C lib/toil/toil-docker docker
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION)-$(TOIL_BUILD_HASH) \
		$(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION);)
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION) \
		$(DOCKER_REGISTRY)/$(MODULE):latest;)
	$(foreach MODULE, $(TOIL_MODULES), docker push $(DOCKER_REGISTRY)/$(MODULE):latest;)
	echo "    finished toil-docker" >> $(LOGFILE)


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
	python ./settings.py
	source ./env.sh; pytest ./etc/tests
