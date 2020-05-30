# Sample Installation Setup as JupyterHub Managed Service

This sample setup uses `docker-compose` to create a JupyterHub environment with `ngshare` and `ngshare_exchange` installed and configured. You will need to adapt this to your own installation. To run this directly as a demo, use `docker-compose build && docker-compose up`.

The `Dockerfile` contains all the installation steps. If you are running JupyterHub on a bare-metal server. you can just run the commands under `RUN` directly on your server, merge `jupyterhub_config.py` with yours, and add `nbgrader_config.py` to `/etc/jupyter`. The `docker-compose.yml` is for simple deployment so you can see ngshare in action on `http://localhost:8000` using `docker-compose build && docker-compose up`.

`jupyterhub_config.py` contains information on how to configure JupyterHub to spawn ngshare. Note that everything after line 9 are for this specific testing setup and should not be included in your config.

`nbgrader_config.py` configures nbgrader to use ngshare_exchange. This should be installed globally by placing it in `/etc/jupyter/`.
