#!make

# import global variables
env ?= .env

include $(env)
include Makefile.authx
export $(shell sed 's/=.*//' $(env))

SHELL = bash
DIR = $(PWD)

#>>>
# option A : set CONDA_INSTALL to $(DIR)/bin to install conda within the candigv2 repo
#  and then use make bin-conda and make init-conda
# option B: set CONDA_INSTALL to the location of an existing miniconda3 installation
#  and then use make mkdir and make init-conda (no bin-conda, which will blow up an existing conda)
# <<<

CONDA_INSTALL = $(DIR)/bin
CONDA = $(CONDA_INSTALL)/miniconda3/bin/conda
CONDA_ENV_SETTINGS = $(CONDA_INSTALL)/miniconda3/etc/profile.d/conda.sh

LOGFILE = $(DIR)/tmp/progress.txt

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
	mkdir -p $(DIR)/tmp/{configs,data,secrets}
	mkdir -p $(DIR)/tmp/{keycloak,tyk,vault}
	mkdir -p ${DIR}/tmp/federation


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
	echo "    started bin-conda" >> $(LOGFILE)
ifeq ($(VENV_OS), linux)
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
	bash $(DIR)/bin/miniconda_install.sh -f -b -u -p $(CONDA_INSTALL)/miniconda3
	# init is needed to create bash aliases for conda but it won't work
	# until you source the script that ships with conda
	source $(CONDA_ENV_SETTINGS) && $(CONDA) init
	echo "    finished bin-conda" >> $(LOGFILE)
endif
ifeq ($(VENV_OS), darwin)
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
	bash $(DIR)/bin/miniconda_install.sh -f -b -u -p $(CONDA_INSTALL)/miniconda3
	# init is needed to create bash aliases for conda but it won't work
	# until you source the script that ships with conda
	source $(CONDA_ENV_SETTINGS) && $(CONDA) init
	echo "    finished bin-conda" >> $(LOGFILE)
endif
ifeq ($(VENV_OS), arm64mac)
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
	bash $(DIR)/bin/miniconda_install.sh -f -b -u -p $(CONDA_INSTALL)/miniconda3
	# init is needed to create bash aliases for conda but it won't work
	# until you source the script that ships with conda
	source $(CONDA_ENV_SETTINGS) && $(CONDA) init zsh
	echo "    finished bin-conda" >> $(LOGFILE)
endif


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
	docker compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml build $(BUILD_OPTS)
	echo "    finished build-$*" >> $(LOGFILE)


#>>>
# run all cleanup functions
# WARNING: these are distructive steps, read through instructions before using
# make clean-all

#<<<
.PHONY: clean-all
clean-all: clean-compose clean-containers clean-secrets \
	clean-volumes clean-images clean-conda clean-bin


#>>>
# clear downloaded binaries
# removes $PWD/bin/
# make clean-bin

#<<<
.PHONY: clean-bin
clean-bin:
	rm -rf $(DIR)/bin


#>>>
# stops and removes docker-compose instances
# make clean-compose

#<<<
.PHONY: clean-compose
clean-compose:
	$(foreach MODULE, $(CANDIG_MODULES), \
		docker compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$(MODULE)/docker-compose.yml down || true;)


#>>>
# deactivate and remove conda env $VENV_NAME
# make clean-conda


#<<<
.PHONY: clean-conda
clean-conda:
	$(CONDA) deactivate
	$(CONDA) env remove -n $(VENV_NAME)


#>>>
# stop all running containers and remove all stopped containers
# make clean-containers

#<<<
.PHONY: clean-containers
clean-containers:
	docker container prune -f


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
	-docker secret rm `docker secret ls -q`
	rm -rf $(DIR)/tmp/secrets


#>>>
# remove all peristant volumes and local data
# make clean-volumes

#<<<
.PHONY: clean-volumes
clean-volumes:
	-docker volume rm `docker volume ls -q`
#rm -rf $(DIR)/tmp/data


#>>>
# deploy/test all modules in $CANDIG_MODULES using docker-compose
# make compose

#<<<
.PHONY: compose
compose:
	$(foreach MODULE, $(CANDIG_MODULES), $(MAKE) compose-$(MODULE);)


#>>>
# deploy/test individual modules using docker-compose
# $module is the name of the sub-folder in lib/
# make compose-$module

#<<<
compose-%:
	echo "    started compose-$*" >> $(LOGFILE)
	docker compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml --compatibility up -d
	echo "    finished compose-$*" >> $(LOGFILE)


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
docker-secrets: mkdir minio-secrets
	@echo admin > $(DIR)/tmp/secrets/metadata-db-user
	$(MAKE) secret-metadata-app-secret
	$(MAKE) secret-metadata-db-secret

	@echo admin > $(DIR)/tmp/secrets/keycloak-admin-user
	$(MAKE) secret-keycloak-admin-password

	@echo user1 > $(DIR)/tmp/secrets/keycloak-test-user
	$(MAKE) secret-keycloak-test-user-password

	@echo user2 > $(DIR)/tmp/secrets/keycloak-test-user2
	$(MAKE) secret-keycloak-test-user2-password

	$(MAKE) secret-tyk-secret-key
	$(MAKE) secret-tyk-node-secret-key
	$(MAKE) secret-tyk-analytics-admin-key

	$(MAKE) secret-vault-s3-token

	$(MAKE) secret-opa-root-token
	$(MAKE) secret-opa-service-token

#>>>
# create persistant volumes for docker containers
# make docker-volumes

#<<<
.PHONY: docker-volumes
docker-volumes:
	docker volume create grafana-data
	docker volume create jupyter-data
	docker volume create minio-config
	docker volume create minio-data $(MINIO_VOLUME_OPT)
	docker volume create prometheus-data
	docker volume create toil-jobstore
	docker volume create keycloak-data
	docker volume create tyk-data
	docker volume create tyk-redis-data
	docker volume create vault-data
	docker volume create opa-data
	docker volume create htsget-data


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
	# source conda's script to be safe, so the conda command is found
	source $(CONDA_ENV_SETTINGS) \
		&& $(CONDA) create -y -n $(VENV_NAME) python=$(VENV_PYTHON) pip=$(VENV_PIP)

	source $(CONDA_ENV_SETTINGS) \
		&& conda activate $(VENV_NAME) \
		&& pip install -U -r $(DIR)/etc/venv/requirements.txt

#@echo "Load local conda: source $(DIR)/bin/miniconda3/etc/profile.d/conda.sh"
#@echo "Activate conda env: conda activate $(VENV_NAME)"
#@echo "Install requirements: pip install -U -r $(DIR)/etc/venv/requirements.txt"
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
		docker compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml pull


#>>>
# push docker image to $DOCKER_REGISTRY
# $module is the name of the sub-folder in lib/
# make push-$module

#<<<
push-%:
		docker compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml push


#>>>
# create a random secret and add it to tmp/secrets/$secret_name
# make secret-$secret_name

#<<<
secret-%:
	@dd if=/dev/urandom bs=1 count=16 2>/dev/null \
		| base64 | tr -d '\n\r+' | sed s/[^A-Za-z0-9]//g > $(DIR)/tmp/secrets/$*


#>>>
# create toil images using upstream CanDIG Toil repo
# make toil-docker

#<<<
.PHONY: toil-docker
toil-docker:
	echo "    started toil-docker" >> $(LOGFILE)
	VIRTUAL_ENV=1 DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 TOIL_DOCKER_REGISTRY=$(DOCKER_REGISTRY) \
	$(MAKE) -C $(DIR)/lib/toil/toil-docker docker
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
# make build-all -P

#<<<
.PHONY: build-all
build-all:
	./pre-build-check.sh

# Setup the entire stack
	$(MAKE) init-docker
	$(MAKE) compose
	$(MAKE) init-authx
