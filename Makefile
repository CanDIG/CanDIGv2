#!make

# import global variables
env ?= .env

include $(env)
include Makefile.authx
export $(shell sed 's/=.*//' $(env))

SHELL = bash
DIR = $(PWD)
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
# (re)build service image and deploy/test using docker-compose
# $module is the name of the sub-folder in lib/
# add BUILD_OPTS='--no-cache' to ignore cached builds
# BUILD_OPTS='--no-cache' make build-$module
# make build-$module

#<<<
build-%:
	echo "    started build-$*" >> $(LOGFILE)
	DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 \
	docker-compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml build $(BUILD_OPTS)
	echo "    finished build-$*" >> $(LOGFILE)


#>>>
# run all cleanup functions
# WARNING: these are distructive steps, read through instructions before using
# make clean-all

#<<<
.PHONY: clean-all
clean-all: clean-compose clean-containers clean-secrets \
	clean-volumes clean-images clean-pipenv


#>>>
# stops and removes docker-compose instances
# make clean-compose

#<<<
.PHONY: clean-compose
clean-compose:
	$(foreach MODULE, $(CANDIG_MODULES), \
		docker-compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$(MODULE)/docker-compose.yml down || true;)


#>>>
# deactivate and remove pipenv venv $VENV_NAME
# make clean-pipenv

#<<<
.PHONY: clean-pipenv
clean-pipenv:
	-`deactivate`
	pipenv --rm


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
	docker-compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml --compatibility up -d
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
# modify the hosts file

#<<<
.PHONY: init-hosts-file
init-hosts-file:
	source ${PWD}/setup_hosts.sh

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
		docker-compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml pull


#>>>
# push docker image to $DOCKER_REGISTRY
# $module is the name of the sub-folder in lib/
# make push-$module

#<<<
push-%:
		docker-compose -f $(DIR)/lib/candigv2/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml push


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

