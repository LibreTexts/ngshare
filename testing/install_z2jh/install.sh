#!/bin/bash -e

# Sample installation script. This is the tl;dr if you don't want to look at the documentation.

# Create a brand new minikube environment. Skip this if you already have a cluster.
minikube delete || true
minikube start

# Add the helm charts for Z2JH and nbgrader
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo add ngshare https://LibreTexts.github.io/ngshare-helm-repo/
helm repo update

# Build custom singleuser image
eval $(minikube docker-env)
docker build -f Dockerfile-singleuser -t ngshare-singleuser-sample:0.0.1 .
eval $(minikube docker-env -u)

# Install Z2JH
helm install jhub jupyterhub/jupyterhub -f config_z2jh.yaml
# For helm2, use
# helm install jupyterhub/jupyterhub -n jhub -f config_z2jh.yaml

# Install ngshare
helm install ngshare ngshare/ngshare -f config_ngshare.yaml
# For helm2, use
# helm install ngshare/ngshare -n ngshare -f config_ngshare.yaml

# We're done!
kubectl get pods
minikube service list
