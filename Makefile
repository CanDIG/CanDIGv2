# import global variables
env ?= .env
include $(env)
export $(shell sed 's/=.*//' $(env))

DIR=$(PWD)

all: clean deploy-all

clean:
	docker stack rm `docker stack ls | awk '{print $1}'`
	docker rm -v `docker ps -aq`
	docker network rm traefik-net
	docker volume rm `docker volume ls -q`
	sudo rm -rf $(DIR)/etc minio_access_key minio_secret_key

consul:
	docker stack deploy --compose-file $(DIR)/lib/consul/consul-server.yml consul

docker-net:
	docker network create --driver overlay --attachable traefik-net

docker-swarm:
	docker swarm init --advertise-addr $(DOCKER_SWARM_IP)

docker-volumes:
	docker volume create minio-config
	docker volume create minio-data
	docker volume create mc-config

dos-connect:
	docker stack deploy --compose-file $(DIR)/lib/dos-connect/dos-connect.yml dos-connect

ga4gh-dos:
	docker stack deploy --compose-file $(DIR)/lib/ga4gh-dos-schemas/ga4gh-dos.yml ga4gh-dos

htsget-client:
	docker stack deploy --compose-file $(DIR)/lib/htsget/htsget-client.yml htsget-client

minio-secrets:
	echo admin > minio_access_key
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > minio_secret_key

minio-server:
	docker stack deploy --compose-file $(DIR)/lib/minio/minio-server.yml minio-server

minio-shell:
	docker stack deploy --compose-file $(DIR)/lib/mc/mc-shell.yml minio-shell

traefik:
	docker stack deploy --compose-file $(DIR)/lib/traefik/traefik-net.yml traefik-net

deploy-all: deploy-net deploy-traefik deploy-minio deploy-dos deploy-htsget
deploy-net: docker-swarm docker-net
deploy-traefik: deploy-net consul traefik-net
deploy-minio: docker-volumes minio-secrets minio-server minio-shell
deploy-dos: ga4gh-dos
deploy-hstget: htsget-client
