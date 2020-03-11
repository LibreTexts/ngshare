# Testing setup

This is the testing / dev environment setup. We have two dev environments, one using Docker (regular JupyterHub without k8s) and one using minikube (Z2JH).

## Preparation
You should clone the following repos in the same folder:
1. [ngshare](https://github.com/lxylxy123456/ngshare) (this repo!)
2. [nbgrader](https://github.com/lxylxy123456/nbgrader), which is built on the [pluggable exchange](https://github.com/jupyter/nbgrader/pull/1238) pull request, with an exchange that works with ngshare.
3. [zero-to-jupyterhub-k8s](https://github.com/rkevin-arch/zero-to-jupyterhub-k8s) (not necessary if only using Docker), which is built on the official Z2JH repo but with ngshare support, and in the near future, the ability to customize k8s-aware hub managed services (WIP).

## Docker
To use the Docker dev environment, you should have [Docker](https://docs.docker.com/install/) and [Docker-compose](https://docs.docker.com/compose/install/) installed.

All you need is to do a `docker-compose build && docker-compose up` in the `testing/docker` directory. After that, JupyterHub should be on port `8000` on `localhost`. You may manually examine the `ngshare` database in `testing/docker/data/ngshare.db`. All changes inside the `nbgrader` repo will also be reflected in Docker immediately for testing.

## minikube

For the k8s dev environment, you need [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) (along with a hypervisor like [VirtualBox](https://www.virtualbox.org/wiki/Downloads)), [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) (no need to configure it; it will be done in `minikube`), [helm](https://helm.sh/docs/intro/install/) (v3), and chartpress(`pip install chartpress`) installed on your system.

Before testing, make sure you run `chartpress` on the `zero-to-jupyterhub-k8s` repo. Simply `cd` into it and run `chartpress`. This only needs to be done once.

To test, simply do the following:
```sh
cd testing/minikube
./test.sh init
./test.sh install
```
This will take a while, but at the end you should see something like this:
```
|-------------|--------------|-----------------------------|-----|
|  NAMESPACE  |     NAME     |         TARGET PORT         | URL |
|-------------|--------------|-----------------------------|-----|
| default     | hub          | No node port                |
| default     | kubernetes   | No node port                |
| default     | proxy-api    | No node port                |
| default     | proxy-public | http://192.168.99.123:31110 |
| kube-system | kube-dns     | No node port                |
|-------------|--------------|-----------------------------|-----|
```
This means you may access and test JupyterHub on `http://192.168.99.123:31110`. Note: for some reason `ngshare` will 404 for around a minute before becoming fully online. We're still trying to identify the issue.

After everything, you may run `./test.sh delete` to delete the minikube environment. You can run `./test.sh` for a list of supported commands.

Note: If you're using a laptop, do not hibernate while `minikube` is running. For some reason, this screws up VirtualBox's port forwarding and you'll have to do `./test.sh delete && ./test.sh init` again.
