#!make

# import global variables
env ?= .env
#overrides ?= site.env

include $(env)
export $(shell sed 's/=.*//' $(env))

#include $(overrides)
#export $(shell sed 's/=.*//' $(overrides))

DIR = $(PWD)
CONDA = $(DIR)/bin/miniconda3/condabin/conda

define help
# view available options
make

# initialize docker and create required docker networks
make init-docker

# initialize docker-compose environment
make init-compose

# initialize conda environment
make init-conda

# initialize kubernetes environment
make init-kubernetes

# initialize docker-swarm environment
make init-swarm

# create docker bridge networks
make docker-net

# push docker images to CanDIG repo
make docker-push

# create docker secrets for CanDIG services
make docker-secrets

# create persistant volumes for docker containers
make docker-volumes

# download all package binaries
make bin-all

# download miniconda package
make bin-conda

# download kubectl (for kubernetes deployment)
make bin-kubectl

# download latest minikube binary from Google repo
make bin-minikube

# download minio server/client
make bin-minio

# generate secrets for minio server/client
make minio-secrets

# create minikube environment for (kubernetes) integration testing
make minikube

# generate root-ca and site ssl certs using openssl
make ssl-cert

# initialize primary docker-swarm master node
make swarm-init

# join a docker swarm cluster using manager/worker token
make swarm-join

# create docker swarm compatbile secrets
make swarm-secrets

# (re)build service image for all modules
make images

# create toil images using upstream Toil repo
make toil-docker

# deploy/test all modules in $$CANDIG_MODULES using docker-compose
make compose

# deploy/test all modules in $$CANDIG_MODULES using docker stack
make stack

# deploy/test all modules in $$CANDIG_MODULES using kubernetes
make kubernetes

# deploy/test all modules in $$CANDIG_MODULES using conda
make conda

# deploys all modules using Tox
make tox

# deploy/test individual modules using conda
# $$module is the name of the sub-folder in lib/
make conda-$$module

# (re)build service image and deploy/test using docker-compose
# $$module is the name of the sub-folder in lib/
make build-$$module

# deploy/test individual modules using docker-compose
# $$module is the name of the sub-folder in lib/
make compose-$$module

# deploy/test indivudual modules using docker stack
# $$module is the name of the sub-folder in lib/
make stack-$$module

# run all cleanup functions
make clean-all

# clear downloaded binaries
make clean-bin

# clear selfsigned-certs
make clean-certs

# stop all running containers and remove all run containers
clean-containers

# clear swarm secrets
clean-secrets

# remove all peristant volumes
clean-volumes

# leave docker-swarm
clean-swarm

# clear container networks
clean-network

# clear all images (including base images)
clean-images

# cleanup for compose, preserves everything except services/containers
clean-compose

# cleanup for stack/kubernetes, preserves everything except stack/services/containers
clean-stack

endef

export help

.PHONY: all
all:
	@printf "$$help"

.PHONY: mkdir
mkdir:
	mkdir -p $(DIR)/bin

# test print global variables
print-%:
	@echo '$*=$($*)'

bin-all: bin-conda bin-kubectl bin-minikube bin-minio

bin-conda: mkdir
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-$(VENV_OS)-x86_64.sh
	bash $(DIR)/bin/miniconda_install.sh -f -b -u -p $(DIR)/bin/miniconda3

bin-kubectl: mkdir
	$(eval KUBECTL_VERSION = \
		$(shell curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt))
	curl -Lo $(DIR)/bin/kubectl \
		https://storage.googleapis.com/kubernetes-release/release/$(KUBECTL_VERSION)/bin/linux/amd64/kubectl
	chmod 755 $(DIR)/bin/kubectl

bin-minikube: mkdir
	curl -Lo $(DIR)/bin/minikube \
		https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
	chmod 755 $(DIR)/bin/minikube

bin-minio: mkdir
	curl -Lo $(DIR)/bin/minio \
		https://dl.minio.io/server/minio/release/linux-amd64/minio
	curl -Lo $(DIR)/bin/mc \
		https://dl.minio.io/client/mc/release/linux-amd64/mc
	chmod 755 $(DIR)/bin/minio
	chmod 755 $(DIR)/bin/mc

bin-traefik: mkdir
	curl -Lo $(DIR)/bin/traefik \
		https://github.com/containous/traefik/releases/download/v$(TRAEFIK_VERSION)/traefik
	chmod 755 $(DIR)/bin/traefik

build-%:
	docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		-f $(DIR)/lib/$*/docker-compose.yml build

.PHONY: clean-all
clean-all: clean-stack clean-containers clean-secrets clean-volumes \
	clean-swarm clean-networks clean-images clean-certs clean-bin

.PHONY: clean-bin
clean-bin:
	rm -rf $(DIR)/bin

.PHONY: clean-certs
clean-certs:
	rm -f $(DIR)/etc/ssl/selfsigned-*

.PHONY: clean-compose
clean-compose: clean-containers

.PHONY: clean-containers
clean-containers:
	docker stop `docker ps -q` || return 0
	docker rm -v `docker ps -aq` || return 0

.PHONY: clean-images
clean-images:
	docker rmi `docker images -q`

.PHONY: clean-network
clean-network:
	docker network rm bridge-net traefik-net agent-net docker_gwbridge

.PHONY: clean-secrets
clean-secrets:
	docker secret rm `docker secret ls -q`
	rm -f minio-access-key minio-secret-key portainer-user portainer-key \
		swarm-manager-token swarm-worker-token

.PHONY: clean-stack
clean-stack:
	docker stack rm `docker stack ls | awk '{print $$1}'`
	$(MAKE) clean-containers

.PHONY: clean-swarm
clean-swarm:
	docker swarm leave --force

.PHONY: clean-volumes
clean-volumes:
	docker volume rm `docker volume ls -q`

.PHONY: compose
compose:
	$(foreach MODULE, $(CANDIG_MODULES), docker-compose -f $(DIR)/lib/compose/docker-compose.yml \
		-f $(DIR)/lib/$(MODULE)/docker-compose.yml up -d;)

compose-%:
	docker-compose -f $(DIR)/lib/compose/docker-compose.yml \
		-f $(DIR)/lib/$*/docker-compose.yml up

.PHONY: conda
conda:
	$(foreach MODULE, $(CONDA_MODULES), screen -dmS $(MODULE) $(DIR)/lib/$(MODULE)/run.sh;)

conda-%:
	screen -dmS $* $(DIR)/lib/$*/run.sh

.PHONY: tox
tox:
	dotenv -f .env run tox

tox-%:
	dotenv -f .env run tox -e $*

.PHONY: docker-net
docker-net:
	docker network create --driver bridge --subnet=$(DOCKER_BRIDGE_IP) --attachable bridge-net
	docker network create --driver bridge --subnet=$(DOCKER_GWBRIDGE_IP) --attachable \
		-o com.docker.network.bridge.enable_icc=false \
		-o com.docker.network.bridge.name=docker_gwbridge \
		-o com.docker.network.bridge.enable_ip_masquerade=true \
		docker_gwbridge

.PHONY: docker-push
docker-push:
	$(foreach MODULE, $(CANDIG_MODULES), docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		-f $(DIR)/lib/$(MODULE)/docker-compose.yml push;)
	$(foreach MODULE, $(TOIL_MODULES), docker push $(TOIL_DOCKER_REGISTRY)/$(MODULE):latest;)

.PHONY: docker-secrets
docker-secrets: minio-secrets
	echo admin > portainer-user
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > portainer-key

.PHONY: docker-volumes
docker-volumes:
	docker volume create minio-config
	docker volume create minio-data $(MINIO_VOLUME_OPT)
	docker volume create mc-config
	docker volume create toil-jobstore
	docker volume create portainer-data
	docker volume create jupyter-data

.PHONY: images
images: toil-docker
	$(foreach MODULE, $(CANDIG_MODULES), docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		-f $(DIR)/lib/$(MODULE)/docker-compose.yml build;)

.PHONY: init-compose
init-compose: docker-secrets

.PHONY: init-conda
init-conda: bin-all minio-secrets
	$(CONDA) create -y -n $(VENV_NAME) python=$(VENV_PYTHON)
	#pip install -r $(DIR)/etc/venv/requirements.txt

.PHONY: init-docker
init-docker: docker-net docker-volumes ssl-cert init-$(DOCKER_MODE)
	git submodule update --init --recursive

.PHONY: init-kubernetes
init-kubernetes: bin-kubectl init-swarm

.PHONY: init-swarm
init-swarm: swarm-init swarm-secrets

.PHONY: kubernetes
kubernetes:
	docker stack deploy \
		--orchestrator $(DOCKER_MODE) \
		--namespace $(DOCKER_NAMESPACE) \
		--compose-file $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		$(foreach MODULE, $(CANDIG_MODULES), --compose-file $(DIR)/lib/$(MODULE)/docker-compose.yml) \
		CanDIGv2

kube-%:
	docker stack deploy \
		--orchestrator $(DOCKER_MODE) \
		--namespace $(DOCKER_NAMESPACE) \
		--compose-file $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		--compose-file $(DIR)/lib/$*/docker-compose.yml \
		$*

.PHONY: minikube
minikube: bin-minikube
	minikube start --bootstrapper kubeadm --container-runtime $(MINIKUBE_CRI) \
		--cpus $(MINIKUBE_CPUS) --memory $(MINIKUBE_MEM) --disk-size $(MINIKUBE_DISK) \
		--network-plugin cni --enable-default-cni --vm-driver $(MINIKUBE_DRIVER)

minio-secrets:
	echo admin > minio-access-key
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > minio-secret-key

ssl-cert:
	openssl genrsa -out $(DIR)/etc/ssl/selfsigned-root-ca.key 4096
	openssl req -new -key $(DIR)/etc/ssl/selfsigned-root-ca.key \
		-out $(DIR)/etc/ssl/selfsigned-root-ca.csr -sha256 \
		-subj '/C=CA/ST=ON/L=Toronto/O=CanDIG/CN=CanDIG Self-Signed CA'
	openssl x509 -req -days 3650 -in $(DIR)/etc/ssl/selfsigned-root-ca.csr \
		-signkey $(DIR)/etc/ssl/selfsigned-root-ca.key -sha256 \
		-out $(DIR)/etc/ssl/selfsigned-root-ca.crt \
		-extfile $(DIR)/etc/ssl/root-ca.cnf -extensions root_ca
	openssl genrsa -out $(DIR)/etc/ssl/selfsigned-site.key 4096
	openssl req -new -key $(DIR)/etc/ssl/selfsigned-site.key \
		-out $(DIR)/etc/ssl/selfsigned-site.csr -sha256 \
		-subj '/C=CA/ST=ON/L=Toronto/O=CanDIG/CN=CanDIG Self-Signed Cert'
	openssl x509 -req -days 750 -in $(DIR)/etc/ssl/selfsigned-site.csr -sha256 \
		-CA $(DIR)/etc/ssl/selfsigned-root-ca.crt \
		-CAkey $(DIR)/etc/ssl/selfsigned-root-ca.key \
		-CAcreateserial -out $(DIR)/etc/ssl/selfsigned-site.crt \
		-extfile $(DIR)/etc/ssl/site.cnf -extensions server

.PHONY: stack
stack:
	docker stack deploy \
		--compose-file $(DIR)/lib/swarm/docker-compose.yml \
		$(foreach MODULE, $(CANDIG_MODULES), --compose-file $(DIR)/lib/$(MODULE)/docker-compose.yml) \
		CanDIGv2

stack-%:
	docker stack deploy \
		--compose-file $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		--compose-file $(DIR)/lib/$*/docker-compose.yml \
		$*

.PHONY: swarm-init
swarm-init:
	docker swarm init --advertise-addr $(SWARM_ADVERTISE_IP) --listen-addr $(SWARM_LISTEN_IP)
	docker swarm join-token manager -q > swarm-manager-token
	docker swarm join-token worker -q > swarm-worker-token
	docker network create --driver overlay --opt encrypted=true traefik-net
	docker network create --driver overlay --opt encrypted=true agent-net

.PHONY: swarm-join
swarm-join:
	docker swarm join --advertise-addr $(SWARM_ADVERTISE_IP) --listen-addr $(SWARM_LISTEN_IP) \
		--token `cat $(DIR)/swarm-$(SWARM_MODE)-token` $(SWARM_MANAGER_IP)

.PHONY: swarm-secrets
swarm-secrets: docker-secrets
	docker secret create minio-access-key $(DIR)/minio-access-key
	docker secret create minio-secret-key $(DIR)/minio-secret-key
	docker secret create portainer-user $(DIR)/portainer-user
	docker secret create portainer-key $(DIR)/portainer-key
	docker secret create traefik-ssl-key $(DIR)/etc/ssl/$(TRAEFIK_SSL_CERT).key
	docker secret create traefik-ssl-crt $(DIR)/etc/ssl/$(TRAEFIK_SSL_CERT).crt
	docker secret create wes-dependency-resolver $(DIR)/etc/yml/$(WES_DEPENDENCY_RESOLVER)

.PHONY: toil-docker
toil-docker:
	VIRTUAL_ENV=1 $(MAKE) -C $(DIR)/lib/toil/toil-docker docker
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(TOIL_DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION)-$(TOIL_BUILD_HASH) \
		$(TOIL_DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION);)
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(TOIL_DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION) \
		$(TOIL_DOCKER_REGISTRY)/$(MODULE):latest;)

