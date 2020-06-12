# Testing setup

These testing setups should allow you to deploy ngshare for simple testing. In particular, the `install_z2jh` and `install_jhmanaged` folders show how to install `ngshare` and `ngshare_exchange` in your Z2JH cluster or as a JupyterHub managed service outside of k8s, respectively.

The `minikube` folder contains some slightly out-of-date instructions on how to install `ngshare` and `ngshare_exchange` from source locally, for testing purposes. You may look at `test.sh` for more details.

The `docker` folder is extremely out of date and should not be used. It was developed back when `ngshare` was not yet ready for Kubernetes.

# NOTE: Everything below is out of date. In particular, we do not need a separate fork for nbgrader anymore. Follow at your own risk.

This is the testing / dev environment setup. We have two dev environments, one using Docker (regular JupyterHub without k8s) and one using minikube (Z2JH).

## Preparation
You should clone the following repos in the same folder:
1. [ngshare](https://github.com/LibreTexts/ngshare) (this repo!)
2. [nbgrader](https://github.com/LibreTexts/nbgrader), which is built on the [pluggable exchange](https://github.com/jupyter/nbgrader/pull/1238) pull request, with an exchange that works with ngshare.

```
git clone https://github.com/LibreTexts/ngshare
git clone https://github.com/LibreTexts/nbgrader
```

## Docker
To use the Docker dev environment, you should have [Docker](https://docs.docker.com/install/) and [Docker-compose](https://docs.docker.com/compose/install/) installed.

All you need is to do a `docker-compose build && docker-compose up` in the `testing/docker` directory. After that, JupyterHub should be on port `8000` on `localhost`. You may manually examine the `ngshare` database in `testing/docker/data/ngshare.db`. All changes inside the `nbgrader` repo will also be reflected in Docker immediately for testing.

## minikube

For the k8s dev environment, you need [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) (along with a hypervisor like [VirtualBox](https://www.virtualbox.org/wiki/Downloads)), [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) (no need to configure it; it will be done in `minikube`), [helm](https://helm.sh/docs/intro/install/) (v3), and chartpress(`pip install chartpress`) installed on your system.

To test, simply do the following:
```sh
cd testing/minikube
./test.sh init
./test.sh install
```
This will take a while, but at the end you should see something like this:
```
|-------------|--------------|--------------|-------------------------|
|  NAMESPACE  |     NAME     | TARGET PORT  |           URL           |
|-------------|--------------|--------------|-------------------------|
| default     | hub          | No node port |
| default     | kubernetes   | No node port |
| default     | ngshare      | No node port |
| default     | proxy-api    | No node port |
| default     | proxy-public |              | http://172.17.0.2:30828 |
| kube-system | kube-dns     | No node port |
|-------------|--------------|--------------|-------------------------|
```
This means you may access and test JupyterHub on `http://172.17.0.2:30828`.

* If Kubenetes is running on a remote server, you may want SSH local forward
 like `-L 127.0.0.1:66666:172.17.0.2:30828`

After everything, you may run `./test.sh delete` to delete the minikube environment. You can run `./test.sh` for a list of supported commands.

Also, you may run `complete -W 'init install uninstall upgrade reinstall delete reboot' ./test.sh` if you have the bash-completion package installed to speed up typing the commands.

Note: If you're using a laptop, do not hibernate while `minikube` is running. For some reason, this screws up VirtualBox's port forwarding and you'll have to do `./test.sh delete && ./test.sh init` again.

Note: Sometimes minikube will crash (port 8443 closed, kubectl say `The connection was refused - did you specify the right host or port?`, and when you go in the VM it shows a lot of systemd services being randomly killed via SIGKILL, including kubelet, dunno why). In that case you don't need to delete the cluster, just rebooting it should work (you might have to manually clean up after an incomplete `helm install` if that's the case, but you can just `kubectl delete pod [podnames]` and start fresh.
