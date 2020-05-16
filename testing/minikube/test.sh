#!/bin/bash -e

# beta.4 is broken for some reason
# ModuleNotFoundError: No module named 'kubernetes'
# File "/etc/jupyterhub/jupyterhub_config.py", line 6: from kubernetes import client
# reverting to beta.3
Z2JH_HELM_CHART_VER=0.9.0
NGSHARE_HELM_CHART_LOC="ngshare/ngshare --version=0.0.1-n295.h86c2be1"

function build_singleuser_img {
    eval $(minikube docker-env)
    docker build -f Dockerfile-singleuser -t singleuser-testing:0.0.1 .
    eval $(minikube docker-env -u)
}

function build_ngshare_img {
    eval $(minikube docker-env)
    cd ../..
    docker build -f Dockerfile -t rkevin/ngshare:0.2.0 .
    cd -
    eval $(minikube docker-env -u)
}

case $1 in
    init )
        # start docker if it isn't started yet, minikube depends on it
        systemctl is-active docker --quiet || sudo systemctl start docker
        minikube start
        helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
        helm repo add ngshare https://rkevin-arch.github.io/ngshare-helm-repo/
        helm repo update ;;
    install )
        build_singleuser_img
        #build_ngshare_img
        helm install jhub jupyterhub/jupyterhub --version=$Z2JH_HELM_CHART_VER -f config.yaml --debug
        helm install ngshare $NGSHARE_HELM_CHART_LOC -f config_ngshare.yaml --debug
        minikube service list ;;
    uninstall )
        helm uninstall jhub
        helm uninstall ngshare ;;
    reinstall )
        helm uninstall jhub
        helm uninstall ngshare
        build_singleuser_img
        #build_ngshare_img
        sleep 10 # sometimes PVCs arent unmounted properly, giving an error when doing helm install
        helm install jhub jupyterhub/jupyterhub --version=$Z2JH_HELM_CHART_LOC -f config.yaml --debug
        helm install ngshare $NGSHARE_HELM_CHART_LOC -f config_ngshare.yaml --debug
        minikube service list ;;
    upgrade )
        build_singleuser_img
        #build_ngshare_img
        helm upgrade jhub jupyterhub/jupyterhub --version=$Z2JH_HELM_CHART_LOC -f config.yaml --debug
        helm upgrade ngshare $NGSHARE_HELM_CHART_LOC -f config_ngshare.yaml --debug
        minikube service list ;;
    pause )
        kubectl scale --replicas=0 deployment ngshare ;;
    resume)
        kubectl scale --replicas=1 deployment ngshare ;;
    copydb )
        scp -i `minikube ssh-key` docker@`minikube ip`:/tmp/hostpath-provisioner/pvc*/ngshare.db /tmp/ngshare.db ;;
    pastedb )
        scp -i `minikube ssh-key` /tmp/ngshare.db docker@`minikube ip`:/tmp/ngshare.db && minikube ssh 'sudo mv /tmp/ngshare.db /tmp/hostpath-provisioner/pvc*/ngshare.db && sudo chown 65535:root /tmp/hostpath-provisioner/pvc*/ngshare.db && sudo chmod 644 /tmp/hostpath-provisioner/pvc*/ngshare.db' ;;
    delete )
        minikube delete ;;
    reboot )
        minikube stop
        minikube start ;;
    *)
        echo "Minikube testing script for ngshare project"
        echo "Usage: $0 COMMAND"
        echo "Available commands:"
        echo "    init: Initializes minikube environment"
        echo "    install: Installs testing setup on minikube"
        echo "    uninstall: Uninstalls testing setup on minikube"
        echo "    upgrade: Updates the testing environment with latest changes. This can be used for fast testing when Z2JH is already installed"
        echo "    reinstall: Does an uninstall and install, for the cases where 'upgrade' doesn't cut it due to messed up pods"
        echo "    delete: Deletes minikube VM, so you can start fresh with init"
        echo "    pause: Pauses ngshare temporarily by disabling the deployment and killing off the pods, allowing you to change the PVC"
        echo "    resume: Resumes ngshare deployment"
        echo "    copydb: Copies the ngshare database to /tmp/ngshare.db so you can modify it"
        echo "    pastedb: Copies the ngshare database from /tmp/ngshare.db into the PVC"
        echo "    delete: Deletes minikube VM, so you can start fresh with init"
        echo "    reboot: Restarts minikube VM, which for some reason occasionally crashes" ;;
esac
