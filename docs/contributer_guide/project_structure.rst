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
``dump.html``, ``home.html``, and ``masonry.min.js`` are for welcome page and database dump page.

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
``ngshare/version.py`` defines current version. It follows `"Single-sourcing the package version" <https://packaging.python.org/guides/single-sourcing-package-version/>`_

Continuous Integration
----------------------
``.travis.yml`` configures continuous integration for unit test and coverage test.

Documentation
-------------
``docs/`` directory contains source code for documentations. See :doc:`docs`.

Deployment
----------
``setup.py`` is for installing and packaging this project.

Testing
-------
``testing/`` is for installing ``ngshare`` in a Kubernetes setup.

This section is under construction
