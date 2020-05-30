Decisions
=========

Technologies Employed
---------------------

When developing ``ngshare``, we used many technologies that are used by other Jupyter projects, especially ``nbgrader`` and `JupyterHub <https://github.com/jupyterhub/jupyterhub>`_. In this way, our project is most likely to be consistent with other Jupyter projects.

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
* `ERAlchemy <https://github.com/Alexis-benoist/eralchemy>`_ - Generate entity
  relation diagrams

Progamming Language
^^^^^^^^^^^^^^^^^^^
* `Python <https://www.python.org/>`_ - The major programming language used to
  develop ``nbgrader``
* `pytest <https://pypi.org/project/pytest/>`_ - Unit test framework
* `pytest-cov <https://pypi.org/project/pytest-cov/>`_ - Code coverage
* `pytest-tornado <https://pypi.org/project/pytest-tornado/>`_ - Test Tornado
  server
* `black <https://github.com/psf/black>`_ - a Python code formatter

Project Management
^^^^^^^^^^^^^^^^^^
* `GitHub <https://github.com/>`_ - a git repository management website
* `Travis CI <https://travis-ci.org/>`_ - Continous integration
* `Codecov <https://codecov.io/>`_ - Code coverage
* `Read the Docs <https://readthedocs.org/>`_ - Documentation

Race Condition
--------------
It is possible to configure multiple ``ngshare`` instances to run at the same time, or allow one ``ngshare`` instance to run in multithread mode. This may trigger an untested race condition and cause an error in production.

We decided to warn users about this when they try to configure ``ngshare`` in this way.

Database Update
---------------
There are a few options on letting whom to update the database:

1. Users must manually use `alembic upgrade head` when ngshare updates,
   otherwise ngshare will refuse to start.
2. ngshare will automatically run alembic upgrade on startup, but the user can
   choose to turn this off using a command line argument.
3. ngshare will automatically run alembic upgrade on startup. The user may not
   disable this.

JupyterHub is using option 2, and we decide to follow this, so that users do not have to perform manual intervention during upgrades. So it is developers' responsibility to make sure Alembic upgrade will not break (e.g. write enough test cases).

To make sure users do not encounter database version problems, we decided to automatically run Alembic upgrade (both schematic and data migration) each time ngshare / vngshare is started. There is little overhead for the version check. We assume that users are regularly backing up their database (e.g. when data migration fails, the database's schema may be updated while ``alembic_version`` is not).
