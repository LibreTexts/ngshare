#!/bin/bash -e

# git repo from https://github.com/rkevin-arch/zero-to-jupyterhub-k8s
HELM_CHART_LOC=../../../zero-to-jupyterhub-k8s/jupyterhub

function build_hub_img {
    eval $(minikube docker-env)
    cd ../..
    docker build -f testing/minikube/Dockerfile-hub -t hub-testing:0.0.1 .
    cd testing/minikube
    eval $(minikube docker-env -u)
}

function build_singleuser_img {
    eval $(minikube docker-env)
    docker build -f Dockerfile-singleuser -t singleuser-testing:0.0.1 .
    eval $(minikube docker-env -u)
}

case $1 in
    init )
        minikube start --memory 5g ;;
    install )
        build_hub_img
        build_singleuser_img
        helm install jhub $HELM_CHART_LOC -f config.yaml --debug
        minikube service list ;;
    uninstall )
        helm uninstall jhub ;;
    reinstall )
        helm uninstall jhub
        build_hub_img
        build_singleuser_img
        sleep 10 # sometimes PVCs arent unmounted properly, giving an error when doing helm install
        helm install jhub $HELM_CHART_LOC -f config.yaml --debug
        minikube service list ;;
    upgrade )
        build_hub_img
        build_singleuser_img
        helm upgrade jhub $HELM_CHART_LOC -f config.yaml --debug
        minikube service list ;;
    delete )
        minikube delete ;;
    *)
        echo "Minikube testing script for ngshare project"
        echo "Usage: $0 COMMAND"
        echo "Available commands:"
        echo "    init: Initializes minikube environment"
        echo "    install: Installs testing setup on minikube"
        echo "    uninstall: Uninstalls testing setup on minikube"
        echo "    upgrade: Updates the testing environment with latest changes. This can be used for fast testing when Z2JH is already installed"
        echo "    reinstall: Does an uninstall and install, for the cases where 'upgrade' doesn't cut it due to messed up pods"
        echo "    delete: Deletes minikube VM, so you can start fresh with init" ;;
esac
