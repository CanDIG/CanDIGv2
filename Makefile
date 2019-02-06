#!make

# import global variables
env ?= .env
include $(env)
export $(shell sed 's/=.*//' $(env))

DIR = $(PWD)
#MODULES = $(shell ls $(DIR)/lib/)
MODULES = consul traefik minio ga4gh-dos htsnexus-server toil igv-js

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


build-%:
	docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml build


clean:
	docker stack rm `docker stack ls | awk '{print $1}'`
	docker stop `docker ps -q`
	docker secret rm `docker secret ls -q`
	docker swarm leave --force
	docker network rm bridge-net traefik-net docker_gwbridge
	docker rm -v `docker ps -aq`
	docker volume rm `docker volume ls -q`
	docker rmi `docker images -q`
	rm -f minio_access_key minio_secret_key


compose:
	$(foreach MODULE, $(MODULES), docker-compose -f $(DIR)/lib/compose/docker-compose.yml -f $(DIR)/lib/$(MODULE)/docker-compose.yml up -d;)


compose-%:
	docker-compose -f $(DIR)/lib/compose/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml up


docker-net:
	docker network create --driver bridge --subnet=$(DOCKER_BRIDGE_IP) --attachable bridge-net
	docker network create --driver bridge --subnet=$(DOCKER_GWBRIDGE_IP) --attachable \
		-o com.docker.network.bridge.enable_icc=false \
		-o com.docker.network.bridge.name=docker_gwbridge \
		-o com.docker.network.bridge.enable_ip_masquerade=true \
		docker_gwbridge


docker-swarm:
	docker swarm init --advertise-addr $(DOCKER_ADVERTISE_IP) --listen-addr $(DOCKER_LISTEN_IP)
	docker network create --driver overlay --ingress --opt encrypted=true traefik-net


docker-volumes:
	docker volume create minio-config
	docker volume create minio-data
	docker volume create mc-config
	docker volume create toil-jobstore


images:
	$(foreach MODULE, $(MODULES), docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml -f $(DIR)/lib/$(MODULE)/docker-compose.yml build;)


init: docker-net docker-volumes docker-swarm minio-secrets


minio-secrets:
	echo admin > minio_access_key
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > minio_secret_key
	docker secret create minio_access_key $(DIR)/minio_access_key
	docker secret create minio_secret_key $(DIR)/minio_secret_key


# test print global variables
print-%:
	@echo '$*=$($*)'


stack:
	docker stack deploy --orchestrator $(DOCKER_MODE) --namespace $(DOCKER_NAMESPACE) --compose-file $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml $(foreach MODULE, $(MODULES), --compose-file $(DIR)/lib/$(MODULE)/docker-compose.yml ) CanDIGv2


stack-%:
	docker stack deploy --orchestrator $(DOCKER_MODE) --namespace $(DOCKER_NAMESPACE) --compose-file $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml --compose-file $(DIR)/lib/$*/docker-compose.yml $*


.PHONY: all clean compose docker-net docker-swarm docker-swarm docker-volumes minio-secrets images init minio-secrets stack


