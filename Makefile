#!make

# import global variables
env ?= .env
include $(env)
export $(shell sed 's/=.*//' $(env))

DIR=$(PWD)

all:

clean:
	docker stack rm `docker stack ls | awk '{print $1}'`
	docker rm -v `docker ps -aq`
	docker network rm bridge-net traefik-net
	docker secret rm `docker secret ls -q`
	docker volume rm `docker volume ls -q`
	docker rmi `docker images -q`
	rm -f minio_access_key minio_secret_key

docker-net:
	docker network create --subnet=10.10.0.0/16 --attachable bridge-net
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

# test print global variables
print-%:
	@echo '$*=$($*)'
