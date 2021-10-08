# CanDIGv2 Install Guide (Kubernetes)

- - -

## Create CanDIGv2 Minikube VM

This method is still experimental but should be able to provide a means to convert existing CanDIGv2 `docker-compose.yml` into native kubernetes service definitions. Using the provided steps will help to create a dev minikube cluster where you can test kubernetes deployments. If the stack successfully deploys on the minikube vm, is stable, and passes all QA steps, it can be reasonably assumed that the `kompose` build will work with other kubernetes clusters (e.g. Azure AKS/Amazon EKS).

The minikube CLI can also be used to provision a multi-vm cluster using the options in `.env`. Modify the `MINIKUBE_*` options in `.env`, then launch a single-node or multi-node kubernetes cluster with `make minikube`. Once minikube is running, set kubectl context to minikube with `$PWD/bin/minikube kubectl`.

## Deploy CanDIGv2 Services (Kubernetes)

```bash
# deploy kubernetes (if using minikube/kubernetes environment)
# requires running minikube vm or kubectl context for existing kubernetes cluster
make init-kubernetes

# deploy CanDIGv2 services
make kubernetes
```

## Cleanup CanDIGv2 Kubernetes Environment

```bash
# 1. stop and remove running kubernetes pods
make clean-kubernetes

# 2. remove all secrets from kubernetes and local dir
make clean-secrets

# 3. destroy minikube instances
make clean-minikube
```

