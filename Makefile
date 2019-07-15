#!make

# import global variables
env ?= .env
overrides ?= site.env

include $(env)
export $(shell sed 's/=.*//' $(env))

#include $(overrides)
#export $(shell sed 's/=.*//' $(overrides))

DIR = $(PWD)
MODULES = weavescope portainer consul traefik minio mc ga4gh-dos htsnexus-server toil igv-js jupyter

define help
# view available options
make

# create python virtualenv for docker-compose and HPC
make virtualenv

# initialize docker and create required docker networks
make init

# initialize docker-compose environment
make init-compose

# initialize docker-swarm environment (alias for swarm-init)
make init-swarm

# initialize kubernetes environment
make init-kubernetes

# create docker bridge networks
make docker-net

# push docker images to CanDIG repo
make docker-push

# create docker secrets for CanDIG services
make docker-secrets

# create persistant volumes for docker containers
make docker-volumes

# download kubectl (for kubernetes deployment)
make kubectl

# download minio server/client
make minio

# generate secrets for minio server/client
make minio-secrets

# download minio server/client and start server start instance
make minio-server

# create minikube environment for integration testing
make minikube

# initialize primary docker-swarm master node
# all other nodes can join in as master/worker
make swarm-init

# join a docker swarm cluster using manager/worker token
make swarm-join

# (re)build service image for all modules in lib/
make images

# create toil images using upstream Toil repo
make toil-docker

# deploy/test all modules in lib/ using docker-compose
make compose

# deploy/test all modules in lib/ using docker stack
make stack

# deploy/test all modules in lib/ using kubernetes
make kubernetes

# (re)build service image and deploy/test using docker-compose
# $$module is the name of the sub-folder in lib/
module=htsget-server
make build-$$module

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

mkdir:
	mkdir -p $(DIR)/bin

build-%:
	docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml -f $(DIR)/lib/$*/docker-compose.yml build

clean:
	docker stack rm `docker stack ls | awk '{print $1}'`
	docker stop `docker ps -q`
	docker secret rm `docker secret ls -q`
	docker swarm leave --force
	docker network rm bridge-net traefik-net agent-net docker_gwbridge
	docker rm -v `docker ps -aq`
	docker volume rm `docker volume ls -q`
	docker rmi `docker images -q`
	rm -f minio_access_key minio_secret_key portainer_user portainer_secret swarm_manager_token swarm_worker_token

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

docker-push:
	$(MAKE) -C $(DIR)/lib/toil/toil-docker push_docker
	$(foreach MODULE, $(MODULES), docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml -f $(DIR)/lib/$(MODULE)/docker-compose.yml push;)

docker-secrets: minio-secrets
	echo admin > portainer_user
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > portainer_key
	docker run --rm httpd:2.4-alpine htpasswd -nbB admin `cat portainer_key` | cut -d ":" -f 2 > $(DIR)/portainer_secret

docker-swarm-secrets: docker-secrets
	docker secret create minio_access_key $(DIR)/minio_access_key
	docker secret create minio_secret_key $(DIR)/minio_secret_key
	docker secret create portainer_user   $(DIR)/portainer_user
	docker secret create portainer_secret $(DIR)/portainer_secret

docker-volumes:
	docker volume create minio-config
	docker volume create minio-data #--opt o=size=$(MINIO_VOLUME_SIZE)
	docker volume create mc-config
	docker volume create toil-jobstore
	docker volume create portainer-data
	docker volume create jupyter-data

images: toil-docker
	$(foreach MODULE, $(MODULES), docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml -f $(DIR)/lib/$(MODULE)/docker-compose.yml build;)
	$(MAKE) docker-push

init: virtualenv docker-net docker-volumes init-$(DOCKER_MODE)

init-compose: docker-secrets

init-kubernetes: kubectl docker-k8snet docker-swarm-secrets

init-swarm: swarm-init docker-swarm-secrets

kubectl: mkdir
	$(eval KUBECTL_VERSION = $(shell curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt))
	curl -Lo $(DIR)/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/$(KUBECTL_VERSION)/bin/linux/amd64/kubectl
	chmod 755 $(DIR)/bin/kubectl

kubernetes:
	docker stack deploy \
		--orchestrator $(DOCKER_MODE) \
		--namespace $(DOCKER_NAMESPACE) \
		--compose-file $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		$(foreach MODULE, $(MODULES), --compose-file $(DIR)/lib/$(MODULE)/docker-compose.yml) \
		CanDIGv2

kube-%:
	docker stack deploy \
		--orchestrator $(DOCKER_MODE) \
		--namespace $(DOCKER_NAMESPACE) \
		--compose-file $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		--compose-file $(DIR)/lib/$*/docker-compose.yml \
		$*

minikube: mkdir
	curl -Lo $(DIR)/bin/minikube \
		https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
	chmod 755 $(DIR)/bin/minikube
	minikube start --bootstrapper kubeadm --container-runtime $(MINIKUBE_CRI) \
	        --cpus $(MINIKUBE_CPUS) --memory $(MINIKUBE_MEM) --disk-size $(MINIKUBE_DISK) \
	        --network-plugin cni --enable-default-cni --vm-driver $(MINIKUBE_DRIVER)

minio: mkdir
	curl -Lo $(DIR)/bin/minio \
		https://dl.minio.io/server/minio/release/linux-amd64/minio
	curl -Lo $(DIR)/bin/mc \
		https://dl.minio.io/client/mc/release/linux-amd64/mc
	chmod 755 $(DIR)/bin/minio
	chmod 755 $(DIR)/bin/mc

minio-secrets:
	echo admin > minio_access_key
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > minio_secret_key

minio-server: #minio minio-secrets
	MINIO_ACCESS_KEY=`cat $(DIR)/minio_access_key` MINIO_SECRET_KEY=`cat $(DIR)/minio_secret_key` \
		$(DIR)/bin/minio server --address $(MINIO_DOMAIN):$(MINIO_PORT) $(MINIO_DATA_DIR) \
		$*

# test print global variables
print-%:
	@echo '$*=$($*)'

stack:
	docker stack deploy \
		--compose-file $(DIR)/lib/swarm/docker-compose.yml \
		$(foreach MODULE, $(MODULES), --compose-file $(DIR)/lib/$(MODULE)/docker-compose.yml) \
		CanDIGv2

stack-%:
	docker stack deploy \
		--compose-file $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		--compose-file $(DIR)/lib/$*/docker-compose.yml \
		$*

swarm-init:
	docker swarm init --advertise-addr $(SWARM_ADVERTISE_IP) --listen-addr $(SWARM_LISTEN_IP)
	docker swarm join-token manager -q > swarm_manager_token
	docker swarm join-token worker -q > swarm_worker_token
	docker network create --driver overlay --opt encrypted=true traefik-net
	docker network create --driver overlay --opt encrypted=true agent-net

swarm-join:
	docker swarm join --advertise-addr $(SWARM_ADVERTISE_IP) --listen-addr $(SWARM_LISTEN_IP) \
		--token `cat $(DIR)/swarm_$(SWARM_MODE)_token` $(SWARM_MANAGER_IP)

toil-docker:
	$(MAKE) -C $(DIR)/lib/toil/toil-docker docker
	$(MAKE) -C $(DIR)/lib/toil/toil-docker push_docker

virtualenv: mkdir
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
	bash $(DIR)/bin/miniconda_install.sh -f -b
	conda create -n $(VENV_NAME) python=$(VENV_PYTHON)
	conda activate $(VENV_NAME)
	pip install -r $(DIR)/etc/venv/requirements.txt

.PHONY: all clean compose docker-net docker-push docker-swarm-secrets docker-volumes \
	images init init-compose init-swarm init-kubernetes kubernetes minikube minio-server \
	stack swarm-init swarm-join toil-docker virtualenv

