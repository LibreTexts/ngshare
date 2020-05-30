# Sample Installation Setup using Z2JH

This sample setup assumes you are using helm3. You may run `install.sh` directly, which will set up a minikube cluster and install Z2JH and ngshare. However, this is just a sample setup, and you should configure ngshare to the specific needs of your cluster.

`install.sh` contains commands to install ngshare and Z2JH.

`config_ngshare.yaml` and `configure_z2jh.yaml` contains the Helm values for the ngshare and Z2JH helm charts.

`Dockerfile-singleuser` is a singleuser image that has `ngshare_exchange` installed and configured. You should merge this with your existing singleuser Dockerfiles. `nbgrader_config.py` is copied into the Docker image.
