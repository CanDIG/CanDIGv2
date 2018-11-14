# import global variables
env ?= .env
include $(env)
export $(shell sed 's/=.*//' $(env))

DIR=$(PWD)

all: clean docker-volumes minio-server minio-shell ga4gh-dos htsget-client

clean:
	docker rm -v `docker ps -aq`
	sudo rm -rf $(DIR)/etc minio_access_key minio_secret_key

docker-net:
	docker network create --driver overlay --attachable traefik_net

docker-swarm:
	docker swarm init --advertise-addr $(DOCKER_SWARM_IP)

docker-volumes:
	docker volume create minio-config
	docker volume create minio-data

minio-secrets:
	echo admin > minio_access_key
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > minio_secret_key

minio-server: minio-secrets
	docker stack deploy --compose-file $(DIR)/lib/minio/minio-server.yml minio_server

minio-shell:
	docker exec -it mc_shell sh

traefik:
	docker stack deploy --compose-file $(DIR)/lib/traefik/traefik-net.yml traefik_net

