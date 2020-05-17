Decisions
=========

This section is under construction

Technologies employed
---------------------

When developing this project, we mostly followed the way ``nbgrader`` and `JupyterHub <https://github.com/jupyterhub/jupyterhub>`_ is designed so that our project is most likely to be accepted by the Jupyter community.

Backend
^^^^^^^
* `JupyterHub <https://github.com/jupyterhub/jupyterhub>`_ - A multi-user
  version of Jupyter Notebook (indirectly used)
* `kubernetes <https://kubernetes.io/>`_ - Underlying container management
  system (indirectly used)
* `minikube <https://kubernetes.io/docs/setup/learning-environment/minikube/>`_ -
  A light-weight testing environment for kubernetes (indirectly used)
* `Tornado web server <https://www.tornadoweb.org/>`_ - A Python web framework
  used in Jupyter community

Database
^^^^^^^^
* `SQLAlchemy <https://www.sqlalchemy.org/>`_ - A Python SQL toolkit
* `SQLite3 <https://www.sqlite.org/index.html>`_ - a light weight database
  engine
* `Alembic <https://alembic.sqlalchemy.org/>`_ - SQLAlchemy migration tool
* `ERAlchemy <https://github.com/Alexis-benoist/eralchemy>`_ - Generate Entity
  Relation Diagrams

Frontend
^^^^^^^^
* `JupyterLab <https://github.com/jupyterlab/jupyterlab>`_ - A new interface for
  Jupyter Notebook (next steps)

Progamming Language
^^^^^^^^^^^^^^^^^^^
* `Python <https://www.python.org/>`_ - The major programming language used to
  develop ``nbgrader``
* `pytest <https://pypi.org/project/pytest/>`_ - Unit test framework
* `pytest-cov <https://pypi.org/project/pytest-cov/>`_ - Code coverage
* `pytest-tornado <https://pypi.org/project/pytest-tornado/>`_ - Test Tornado
  server
* `black <https://github.com/psf/black>`_ - a Python code formatter

Project management
^^^^^^^^^^^^^^^^^^
* `GitHub <https://github.com/>`_ - a git repository management website
* `Travis CI <https://travis-ci.org/>`_ - Continous integration
* `Codecov <https://codecov.io/>`_ - Code coverage
* `Read the Docs <https://readthedocs.org/>`_ - Documentation

Race Condition
--------------
It is possible to configure multiple ``ngshare`` instances to run at the same time, or allow one ``ngshare`` instance to run in multithread mode. This may trigger untested race condition and cause error in production.

We decide to warn users about this when they try to configure ``ngshare`` in this way.

Database Update
---------------
To make sure users do not encounter database version problems, we decide to automatically run Alembic upgrade each time ngshare / vngshare is started. There is little overhead for the version check. We assume that users are regularly backing up their database. 
