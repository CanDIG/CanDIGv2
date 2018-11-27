#!make

# import global variables
env ?= .env
include $(env)
export $(shell sed 's/=.*//' $(env))

DIR = $(PWD)
MODULES = $(shell ls $(DIR)/lib/)

all:
	@echo '# view available options'
	@echo 'make'
	@echo
	@echo '# initialize docker swarm and create required docker networks'
	@echo 'make init'
	@echo
	@echo '# deploy/test all modules in lib/ using docker-compose'
	@echo 'make compose'
	@echo
	@echo '# deploy/test all modules in lib/ using docker stack'
	@echo 'make stack'
	@echo
	@echo '# (re)build service image and deploy/test using docker-compose'
	@echo '# $$module is the name of the sub-folder in lib/'
	@echo 'module=htsget-server'
	@echo 'make build-$$module'
	@echo
	@echo '# deploy/test individual modules using docker-compose'
	@echo '# $$module is the name of the sub-folder in lib/'
	@echo 'module=ga4gh-dos'
	@echo 'make compose-$$module'
	@echo
	@echo '# deploy/test indivudual modules using docker stack'
	@echo '# $$module is the name of the sub-folder in lib/'
	@echo 'module=igv-js'
	@echo 'make stack-$$module'
	@echo
	@echo '# cleanup environment'
	@echo 'make clean'


clean:
	docker stack rm `docker stack ls | awk '{print $1}'`
	docker rm -v `docker ps -aq`
	docker network rm bridge-net traefik-net
	docker secret rm `docker secret ls -q`
	docker volume rm `docker volume ls -q`
	docker rmi `docker images -q`
	rm -f minio_access_key minio_secret_key


compose:
	docker-compose $(foreach MODULE, $(MODULES), -f $(DIR)/lib/$(MODULE)/docker-compose.yml ) up


stack:
	docker stack deploy $(foreach MODULE, $(MODULES), --compose-file $(DIR)/lib/$(MODULE)/docker-compose.yml ) CanDIGv2


build-%:
	docker-compose -f $(DIR)/lib/$*/docker-compose.yml build


docker-net:
	docker network create --driver bridge --subnet=10.10.0.0/16 --attachable bridge-net
	docker network create --driver overlay --opt encrypted --attachable traefik-net


docker-swarm:
	docker swarm init --advertise-addr $(DOCKER_SWARM_IP)


docker-volumes:
	docker volume create minio-config
	docker volume create minio-data
	docker volume create mc-config


compose-%:
	docker-compose -f $(DIR)/lib/$*/docker-compose.yml up


stack-%:
	docker stack deploy --compose-file $(DIR)/lib/$*/docker-compose.yml $*


minio-secrets:
	echo admin > minio_access_key
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > minio_secret_key
	docker secret create minio_access_key minio_access_key
	docker secret create minio_secret_key minio_secret_key


init: docker-swarm docker-net docker-volumes minio-secrets


# test print global variables
print-%:
	@echo '$*=$($*)'

.PHONY all clean compose stack docker-net docker-swarm docker-swarm docker-volumes minio-secrets init
