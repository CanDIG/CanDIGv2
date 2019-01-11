#!make

# import global variables
env ?= .env
include $(env)
export $(shell sed 's/=.*//' $(env))

DIR = $(PWD)
#MODULES = $(shell ls $(DIR)/lib/)
MODULES = consul traefik minio ga4gh-dos htsnexus-server igv-js

define help
# view available options
make

# initialize docker swarm and create required docker networks
make init

# deploy/test all modules in lib/ using docker-compose
make compose

# deploy/test all modules in lib/ using docker stack
make stack

# (re)build service image and deploy/test using docker-compose
# $$module is the name of the sub-folder in lib/
module=htsget-server
make build-$$module

# (re)build service image for all modules in lib/
make images

# deploy/test individual modules using docker-compose
# $$module is the name of the sub-folder in lib/
module=ga4gh-dos
make compose-$$module

# deploy/test indivudual modules using docker stack
# $$module is the name of the sub-folder in lib/
module=igv-js
make stack-$$module

# cleanup environment
make clean

endef

export help

all:
	@printf "$$help"

clean:
	docker stack rm `docker stack ls | awk '{print $1}'`
	docker rm -v `docker ps -aq`
	docker network rm bridge-net traefik-net
	docker secret rm `docker secret ls -q`
	docker volume rm `docker volume ls -q`
	docker rmi `docker images -q`
	rm -f minio_access_key minio_secret_key


compose:
	$(foreach MODULE, $(MODULES), docker-compose -f $(DIR)/lib/compose/docker-compose.yml -f $(DIR)/lib/$(MODULE)/docker-compose.yml up -d;)


stack:
	docker stack deploy --compose-file $(DIR)/lib/swarm/docker-compose.yml $(foreach MODULE, $(MODULES), --compose-file $(DIR)/lib/$(MODULE)/docker-compose.yml ) CanDIGv2


build-%:
	docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml build

images:
	$(foreach MODULE, $(MODULES), docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml -f $(DIR)/lib/$(MODULE)/docker-compose.yml build;)


docker-net:
	docker network create --driver bridge --subnet=10.10.1.0/24 --attachable bridge-net
	docker network create --driver bridge --subnet=10.10.2.0/24 --attachable \
		-o com.docker.network.bridge.enable_icc=false \
		-o com.docker.network.bridge.name=docker_gwbridge \
		-o com.docker.network.bridge.enable_ip_masquerade=true \
		docker_gwbridge


docker-swarm:
	docker swarm init --advertise-addr $(DOCKER_SWARM_IP)
	docker network create --driver overlay --opt encrypted --attachable traefik-net


docker-volumes:
	docker volume create minio-config
	docker volume create minio-data
	docker volume create mc-config


compose-%:
	docker-compose -f $(DIR)/lib/compose/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml up


stack-%:
	docker stack deploy --compose-file $(DIR)/lib/swarm/docker-compose.yml --compose-file $(DIR)/lib/$*/docker-compose.yml $*


minio-secrets:
	echo admin > minio_access_key
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > minio_secret_key
	docker secret create minio_access_key $(DIR)/minio_access_key
	docker secret create minio_secret_key $(DIR)/minio_secret_key


init: docker-net docker-volumes docker-swarm minio-secrets


# test print global variables
print-%:
	@echo '$*=$($*)'

.PHONY: all clean compose stack docker-net docker-swarm docker-swarm docker-volumes minio-secrets init images
