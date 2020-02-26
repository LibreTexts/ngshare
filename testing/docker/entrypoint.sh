#!/bin/bash -e

# Installs nbgrader. Should be run inside the Docker container.

cd /srv/src/nbgrader

pip install -r dev-requirements.txt -e .

jupyter nbextension install --symlink --sys-prefix --py nbgrader
jupyter nbextension enable --sys-prefix --py nbgrader
jupyter serverextension enable --sys-prefix --py nbgrader


# Then start jupyterhub

cd -
jupyterhub
