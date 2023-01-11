#!/bin/bash -e

# Installs nbgrader. Should be run inside the Docker container.

cd /srv/src/nbgrader

pip install -e .

# Then start jupyterhub

cd -
jupyterhub
