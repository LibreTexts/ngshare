# Setting up dev environment using minikube

# WARNING: This is way out of date.

TODO: update this. For now, the tl;dr is just run `./test.sh`. You might have to run `chartpress` in the Helm chart repo the first time, too.

Also, for some reason I keep getting weird 404s in the web UI. From what I can tell it's just the proxy being really slow at adding the route in correctly or something. Just be patient and wait like 5 mins. Also, occasionally all the connections go super slow, and connections just randomly hang and throw out "service unavailable" messages, and it runs out of memory constantly. Not sure if it's my fault, but the current setup sort of works.

# Everything below is deprecated.

## Step 0: Install VirtualBox or KVM or something similar

You should have already done this.

## Step 1: Install minikube, kubectl and helm on your host

Exact steps differ between systems. I'm using Arch Linux, so all I did was installing `minikube` and `kubectl`, and installed the `kubernetes-helm` AUR package.

```sh
pacman -S minikube kubectl
git clone https://aur.archlinux.org/kubernetes-helm.git
cd kubernetes-helm
makepkg
pacman -U kubernetes-helm-3.0.3-1-x86_64.pkg.tar.xz
```

For Fedora, to install `minikube`, use

```sh
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-1.6.2.rpm \
 && sudo rpm -ivh minikube-1.6.2.rpm
```

Your system may differ.

## Step 2: Fetch the JupyterHub helm chart

```sh
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update
```

This only needs to be done once.

## Step 3: Start the minikube cluster

Run `minikube start --memory=5g`. If you give it 2GB of memory, it refuses to start. If you give it 3GB, you can login as one user, but you can't login as a second one. If you give it 4GB, you can login as two users, but not a third one. 5GB seems to be a safe amount, supporting up to 3 users, which should be enough for testing.

Other Options
* `--disk-size=20000mb`
* `--vm-driver virtualbox`

## Step 4: Install JupyterHub

Run `helm install jhub jupyterhub/jupyterhub -f config.yaml`. This might take a while with no output, stay calm! You should already have a `config.yaml` in the `minikube_devenv` directory, or you can create one as follows if you're paranoid...

```yaml
proxy:
  secretToken: "HERES_A_VERY_SECRET_TOKEN"
```

... where the secret token should be 32 random bytes converted to hex values (a string of length 64). You can generate it using `openssl rand -hex 32`. The secret token doesn't have to be that secret in this case since this is only a local dev setup.

## Step 5: Use it!

You can open the URL of the JupyterHub instance by running `minikube service proxy-public`. You can use any username and password, since this is a dev environment. Using different usernames will give you different workspaces, and using the same username should give you the same workspace.

Also, if you want fancy monitoring, you can run `minikube dashboard`. It shouldn't be necessary, though.

If you are working on a server with a ssh connection, you can use `-L local_port:127.0.0.1:remote_port` to forward connection to local port to remote port. 

For example, if `minikube service proxy-public` gives `http://192.168.99.100:31923` and `minikube dashboard` gives `http://127.0.0.1:35179`, then you can use the following ssh arguments to be able to access these pages through your browser. 
```
-L 31923:192.168.99.100:31923
-L 35179:127.0.0.1:35179
```

## Step 6: Tearing stuff down

You can run `minikube stop` to temporarily stop the VM, and `minikube start` to restart it. If you want to destroy everything and start anew, use `minikube delete`. You need to redo `helm install` again, although you don't need to do step 2.
