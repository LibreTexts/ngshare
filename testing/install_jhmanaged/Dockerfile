FROM jupyterhub/jupyterhub

# Sample installation instructions for regular JupyterHub

# Some boilerplate code to setup a working environment
RUN apt update && apt install -y git
RUN useradd -m -s /bin/sh user

# Install ngshare
RUN python3 -m pip install ngshare

# Configure JupyterHub to spawn ngshare
COPY jupyterhub_config.py .

# Install nbgrader
RUN python3 -m pip install git+https://github.com/jupyter/nbgrader.git@5a81fd5 && \
    jupyter nbextension install --symlink --sys-prefix --py nbgrader && \
    jupyter nbextension enable --sys-prefix --py nbgrader && \
    jupyter serverextension enable --sys-prefix --py nbgrader

# Install ngshare_exchange
RUN python3 -m pip install ngshare_exchange

# Configure nbgrader
COPY nbgrader_config.py /etc/jupyter/nbgrader_config.py

# That's it!
