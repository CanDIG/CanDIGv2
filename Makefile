#!make

# import global variables
env ?= .env
#overrides ?= site.env

include $(env)
export $(shell sed 's/=.*//' $(env))

#include $(overrides)
#export $(shell sed 's/=.*//' $(overrides))

SHELL = bash
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

# pull images from $$DOCKER_REGISTRY
make docker-pull

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

#download kompose (for kubernetes deployment)
make bin-kompose

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

# deploys individual module using tox
# $$module is the name of the sub-folder in lib
make tox-$$module

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

# clear conda environment and secrets
make clean-conda

# stop all running containers and remove all run containers
clean-containers

# clear all screen sessions
make clean-screens

# clear swarm secrets
make clean-secrets

# remove all peristant volumes
make clean-volumes

# leave docker-swarm
make clean-swarm

# clear container networks
make clean-networks

# clear all images (including base images)
make clean-images

# cleanup for compose, preserves everything except services/containers
make clean-compose

# cleanup for stack/kubernetes, preserves everything except stack/services/containers
make clean-stack

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

bin-all: bin-conda bin-kompose bin-kubectl bin-minikube bin-minio bin-prometheus

bin-conda: mkdir
ifeq ($(VENV_OS), linux)
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
endif
ifeq ($(VENV_OS), darwin)
	curl -Lo $(DIR)/bin/miniconda_install.sh \
		https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
endif
	bash $(DIR)/bin/miniconda_install.sh -f -b -u -p $(DIR)/bin/miniconda3

bin-kompose: mkdir
	curl -L https://github.com/kubernetes/kompose/releases/download/v1.21.0/kompose-$(VENV_OS)-amd64 -o $(DIR)/bin/kompose
	chmod 755 $(DIR)/bin/kubectl

bin-kubectl: mkdir
	$(eval KUBECTL_VERSION = \
		$(shell curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt))
	curl -Lo $(DIR)/bin/kubectl \
		https://storage.googleapis.com/kubernetes-release/release/$(KUBECTL_VERSION)/bin/$(VENV_OS)/amd64/kubectl
	chmod 755 $(DIR)/bin/kubectl

bin-minikube: mkdir
	curl -Lo $(DIR)/bin/minikube \
		https://storage.googleapis.com/minikube/releases/latest/minikube-$(VENV_OS)-amd64
	chmod 755 $(DIR)/bin/minikube

bin-minio: mkdir
	curl -Lo $(DIR)/bin/minio \
		https://dl.minio.io/server/minio/release/$(VENV_OS)-amd64/minio
	curl -Lo $(DIR)/bin/mc \
		https://dl.minio.io/client/mc/release/$(VENV_OS)-amd64/mc
	chmod 755 $(DIR)/bin/minio
	chmod 755 $(DIR)/bin/mc

bin-prometheus:
	mkdir -p $(DIR)/bin/prometheus
	curl -Lo $(DIR)/bin/prometheus/temp.tar.gz https://github.com/prometheus/prometheus/releases/download/v$(PROMETHEUS_VERSION)/prometheus-$(PROMETHEUS_VERSION).$(VENV_OS)-amd64.tar.gz
	tar --strip-components=1 -zxvf $(DIR)/bin/prometheus/temp.tar.gz -C $(DIR)/bin/prometheus
	rm $(DIR)/bin/prometheus/temp.tar.gz
	chmod 755 $(DIR)/bin/prometheus/prometheus

bin-traefik: mkdir
	curl -Lo $(DIR)/bin/traefik \
		https://github.com/containous/traefik/releases/download/v$(TRAEFIK_VERSION)/traefik
	chmod 755 $(DIR)/bin/traefik

build-%:
	DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		-f $(DIR)/lib/$*/docker-compose.yml build --no-cache

.PHONY: clean-all
clean-all: clean-stack clean-containers clean-secrets clean-volumes \
	clean-swarm clean-networks clean-images clean-certs clean-conda clean-bin

.PHONY: clean-bin
clean-bin:
	rm -rf $(DIR)/bin

.PHONY: clean-certs
clean-certs:
	rm -f $(DIR)/etc/ssl/selfsigned-*

.PHONY: clean-compose
clean-compose: clean-containers

.PHONY: clean-conda
clean-conda:
	$(CONDA) deactivate
	$(CONDA) env remove -n $(VENV_NAME)
	rm -f minio-access-key minio-secret-key aws-credentials

.PHONY: clean-containers
clean-containers:
	docker stop `docker ps -q`
	docker container prune -f

.PHONY: clean-images
clean-images:
	docker image prune -a -f

.PHONY: clean-kubernetes
clean-kubernetes:
	$(DIR)/bin/kompose --file $(DIR)/lib/kubernetes/docker-compose.yml \
		$(foreach MODULE, $(CANDIG_MODULES), --file $(DIR)/lib/$(MODULE)/docker-compose.yml) \
		down

.PHONY: clean-minikube
clean-minikube:
	$(DIR)/bin/minikube delete

.PHONY: clean-networks
clean-networks:
	docker network prune -f

.PHONY: clean-secrets
clean-secrets:
	docker secret rm `docker secret ls -q`
	rm -f minio-access-key minio-secret-key aws-credentials \
		portainer-user portainer-key swarm-manager-token swarm-worker-token

.PHONY: clean-screens
clean-screens:
	screen -ls | grep pts | cut -d. -f1 | awk '{print $$1}' | xargs kill

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
	git submodule update --init --recursive
	dotenv -f .env run tox -e $*

.PHONY: docker-net
docker-net:
	docker network create --driver bridge --subnet=$(DOCKER_BRIDGE_IP) --attachable bridge-net
	docker network create --driver bridge --subnet=$(DOCKER_GWBRIDGE_IP) --attachable \
		-o com.docker.network.bridge.enable_icc=false \
		-o com.docker.network.bridge.name=docker_gwbridge \
		-o com.docker.network.bridge.enable_ip_masquerade=true \
		docker_gwbridge

.PHONY: docker-pull
docker-pull:
	$(foreach MODULE, $(CANDIG_MODULES), docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		-f $(DIR)/lib/$(MODULE)/docker-compose.yml pull;)
	$(foreach MODULE, $(TOIL_MODULES), docker pull $(DOCKER_REGISTRY)/$(MODULE):latest;)

.PHONY: docker-push
docker-push:
	$(foreach MODULE, $(CANDIG_MODULES), docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		-f $(DIR)/lib/$(MODULE)/docker-compose.yml push;)
	$(foreach MODULE, $(TOIL_MODULES), docker push $(DOCKER_REGISTRY)/$(MODULE):latest;)

.PHONY: docker-secrets
docker-secrets: minio-secrets
	echo admin > portainer-user
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > portainer-key

.PHONY: docker-volumes
docker-volumes:
	docker volume create datasets-data
	docker volume create minio-config
	docker volume create minio-data $(MINIO_VOLUME_OPT)
	docker volume create mc-config
	docker volume create toil-jobstore
	docker volume create portainer-data
	docker volume create prometheus-data
	docker volume create jupyter-data

.PHONY: images
images: toil-docker
	$(foreach MODULE, $(CANDIG_MODULES), DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		-f $(DIR)/lib/$(MODULE)/docker-compose.yml build;)

.PHONY: init-compose
init-compose: docker-secrets

.PHONY: init-conda
init-conda: bin-all minio-secrets
	$(CONDA) create -y -n $(VENV_NAME) python=$(VENV_PYTHON)
	@echo "Load local conda: source $(DIR)/bin/miniconda3/etc/profile.d/conda.sh"
	@echo "Activate conda env: conda activate $(VENV_NAME)"
	@echo "Install requirements: pip install -r $(DIR)/etc/venv/requirements.txt"

# NOTE: make init-singularity? @p :0
.PHONY: init-docker
init-docker: docker-net docker-volumes ssl-cert init-$(DOCKER_MODE) init-conda
	git submodule update --init --recursive

.PHONY: init-kubernetes
init-kubernetes: bin-all
	$(DIR)/bin/kubectl create namespace candig


.PHONY: init-swarm
init-swarm: swarm-init swarm-net swarm-secrets

.PHONY: kubernetes
kubernetes:
	$(DIR)/bin/kompose --file $(DIR)/lib/kubernetes/docker-compose.yml \
		$(foreach MODULE, $(CANDIG_MODULES), --file $(DIR)/lib/$(MODULE)/docker-compose.yml) \
		up

	# docker stack deploy \
	# 	--orchestrator $(DOCKER_MODE) \
	# 	--namespace $(DOCKER_NAMESPACE) \
	# 	--compose-file $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
	# 	$(foreach MODULE, $(CANDIG_MODULES), --compose-file $(DIR)/lib/$(MODULE)/docker-compose.yml) \
	# 	CanDIGv2

kube-%:
	$(DIR)/bin/kompose --file $(DIR)/lib/kubernetes/docker-compose.yml \
		--file $(DIR)/lib/$*/docker-compose.yml up

.PHONY: minikube
minikube:
	$(DIR)/bin/minikube start --container-runtime $(MINIKUBE_CRI) \
		--cpus $(MINIKUBE_CPUS) --memory $(MINIKUBE_MEM) --disk-size $(MINIKUBE_DISK) \
		--network-plugin cni --cni $(MINIKUBE_CNI) --driver $(MINIKUBE_DRIVER) \
		--dns-domain $(CANDIG_DOMAIN) --nodes $(MINIKUBE_NODES)

minio-secrets:
	echo admin > minio-access-key
	dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev > minio-secret-key
	echo '[default]' > aws-credentials
	echo "aws_access_key_id=`cat minio-access-key`" >> aws-credentials
	echo "aws_secret_access_key=`cat minio-secret-key`" >> aws-credentials

push-%:
	docker-compose \
		-f $(DIR)/lib/$(DOCKER_MODE)/docker-compose.yml \
		-f $(DIR)/lib/$*/docker-compose.yml push

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
		--compose-file $(DIR)/lib/swarm/docker-compose.yml \
		--compose-file $(DIR)/lib/$*/docker-compose.yml CanDIGv2

.PHONY: swarm-init
swarm-init:
	docker swarm init --advertise-addr $(SWARM_ADVERTISE_IP) --listen-addr $(SWARM_LISTEN_IP)
	docker swarm join-token manager -q > swarm-manager-token
	docker swarm join-token worker -q > swarm-worker-token

.PHONY: swarm-join
swarm-join:
	docker swarm join --advertise-addr $(SWARM_ADVERTISE_IP) --listen-addr $(SWARM_LISTEN_IP) \
		--token `cat $(DIR)/swarm-$(SWARM_MODE)-token` $(SWARM_MANAGER_IP)

.PHONY: swarm-net
swarm-net:
	docker network create --driver overlay --opt encrypted=true traefik-net
	docker network create --driver overlay --internal --opt encrypted=true agent-net

.PHONY: swarm-secrets
swarm-secrets: docker-secrets
	docker secret create minio-access-key $(DIR)/minio-access-key
	docker secret create minio-secret-key $(DIR)/minio-secret-key
	docker secret create aws-credentials $(DIR)/aws-credentials
	docker secret create portainer-user $(DIR)/portainer-user
	docker secret create portainer-key $(DIR)/portainer-key
	docker secret create traefik-ssl-key $(DIR)/etc/ssl/$(TRAEFIK_SSL_CERT).key
	docker secret create traefik-ssl-crt $(DIR)/etc/ssl/$(TRAEFIK_SSL_CERT).crt
	docker secret create wes-dependency-resolver $(DIR)/etc/yml/$(WES_DEPENDENCY_RESOLVER)

.PHONY: toil-docker
toil-docker:
	VIRTUAL_ENV=1 DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 TOIL_DOCKER_REGISTRY=$(DOCKER_REGISTRY) $(MAKE) -C $(DIR)/lib/toil/toil-docker docker
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION)-$(TOIL_BUILD_HASH) \
		$(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION);)
	$(foreach MODULE,$(TOIL_MODULES), \
		docker tag $(DOCKER_REGISTRY)/$(MODULE):$(TOIL_VERSION) \
		$(DOCKER_REGISTRY)/$(MODULE):latest;)

