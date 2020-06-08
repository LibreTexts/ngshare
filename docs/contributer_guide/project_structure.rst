Project Structure
=================

ngshare
-------
``ngshare/`` directory contains Tornado web server code for ngshare.

Python scripts
^^^^^^^^^^^^^^
``ngshare.py`` is the Tornado web server code for ngshare.

``vngshare.py`` is a Python script for starting ``vngshare``. See :doc:`vngshare`.

Unit tests
^^^^^^^^^^
``test_ngshare.py`` defines unit tests for ``ngshare``.

``database/test_database.py`` defines unit tests for database structure.

``test_dbutil.py`` defines unit tests for database migration.

HTML and JS
^^^^^^^^^^^
``dump.html``, ``home.html``, and ``masonry.min.js`` are for the welcome page and database dump page.

Favicon
^^^^^^^
``favicon.ico``, ``favicon.png``, and ``favicon.svg`` are the icon for ngshare in different file formats.

Database
^^^^^^^^
The database structure is defined in ``database/``. See :doc:`database`.

Alembic
^^^^^^^
``alembic/``, ``alembic.ini``, and ``dbutil.py`` are for database migration. See :doc:`alembic`.

Version Number
--------------
``ngshare/version.py`` defines the current version. It follows `"Single-sourcing the package version" <https://packaging.python.org/guides/single-sourcing-package-version/>`_

Continuous Integration
----------------------
``.travis.yml`` configures continuous integration for unit test and coverage test.

Documentation
-------------
``docs/`` directory contains source code for documentation. See :doc:`docs`.

Deployment
----------
``setup.py`` is for installing and packaging this project.

Testing
-------
``testing/`` contains setups used for testing ngshare, ngshare_exchange, nbgrader, and Z2JH.

``testing/docker`` contains a Docker environment for initial testing. It is slightly out of date and still uses our fork of ngshare rather than ngshare_exchange.

``testing/minikube`` contains a minikube environment. This is the main testing setup for local development, and it uses ngshare and ngshare_exchange on the local filesystem.

``testing/install_jhmanaged`` contains a Docker environment that demonstrates how a regular user would install ngshare and ngshare_exchange.

``testing/install_z2jh`` contains a minikube environment that demonstrates how a regular user would install ngshare and ngshare_exchange on a standard Kubernetes cluster.

ngshare_exchange
----------------
The client side of ngshare is packaged into a `separate repo <https://github.com/LibreTexts/ngshare_exchange>`_.

``ngshare_exchange/*.py`` implement a nbgrader pluggable exchange that uses ngshare to release, fetch, and submit assignments.

``ngshare_exchange/course_management.py`` will be installed as the ``ngshare-course-management`` command. It is used for admins and instructors to manage course rosters.
