#!make

# import global variables
env ?= .env
overrides ?= site.env

include $(env)
export $(shell sed 's/=.*//' $(env))

include $(overrides)
export $(shell sed 's/=.*//' $(overrides))

DIR = $(PWD)
#MODULES = $(shell ls $(DIR)/lib/)
MODULES = portainer consul traefik minio mc ga4gh-dos htsnexus-server toil igv-js jupyter

define help
# view available options
make

# initialize docker and create required docker networks
make init

# join a docker swarm cluster using manager/worker token
make swarm-join

# (re)build service image for all modules in lib/
make images

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

docker-volumes:
	docker volume create minio-config
	docker volume create minio-data --opt o=size=$(MINIO_VOLUME_SIZE)
	docker volume create mc-config
	docker volume create toil-jobstore
	docker volume create portainer_data

images:
	$(foreach MODULE, $(MODULES), docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml -f $(DIR)/lib/$(MODULE)/docker-compose.yml build;)

init: virtualenv docker-net docker-volumes init-$(DOCKER_MODE)

init-compose: minio-secrets

init-swarm: swarm-init minio-secrets

init-kubernetes: kubectl minikube minio-secrets

kubectl:
	mkdir -p $(DIR)/bin
	curl -LOo $(DIR)/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
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

minikube:
	mkdir -p $(DIR)/bin
	curl -Lo $(DIR)/bin/minikube \
		https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
	chmod 755 $(DIR)/bin/minikube
	minikube start --bootstrapper kubeadm --container-runtime $(MINIKUBE_CRI) \
	        --cpus $(MINIKUBE_CPUS) --memory $(MINIKUBE_MEM) --disk-size $(MINIKUBE_DISK) \
	        --network-plugin cni --enable-default-cni --vm-driver $(MINIKUBE_DRIVER)

minio-secrets:
	echo admin > minio_access_key
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > minio_secret_key
	echo admin > portainer_user
	docker run --rm httpd:2.4-alpine htpasswd -nbB admin \
		$(dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev) \
		| cut -d ":" -f 2 > $(DIR)/portainer_secret
	docker secret create minio_access_key $(DIR)/minio_access_key
	docker secret create minio_secret_key $(DIR)/minio_secret_key
	docker secret create portainer_user   $(DIR)/portainer_user
	docker secret create portainer_secret $(DIR)/portainer_secret

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
	docker network create --driver overlay --opt encrypted=true agent_network

swarm-join:
	docker swarm join --advertise-addr $(SWARM_ADVERTISE_IP) --listen-addr $(SWARM_LISTEN_IP) \
		--token `cat $(DIR)/swarm_$(SWARM_MODE)_token` $(SWARM_MANAGER_IP)

virtualenv:
	mkdir -p $(DIR)/bin
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
	bash $(DIR)/bin/miniconda_install.sh -f -b
	source $(HOME)/miniconda3/etc/profile.d/conda.sh
	conda create -y -n $(VENV_NAME) python=$(VENV_PYTHON)
	conda activate $(VENV_NAME)
	pip install -r $(DIR)/lib/venv/requirements.txt

.PHONY: all clean compose docker-net docker-volumes images init init-compose init-swarm init-kubernetes \
	kubectl kubernetes minikube minio-secrets stack swarm-init swarm-join virtualenv


