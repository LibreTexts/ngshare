ngshare
=======

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://travis-ci.org/lxylxy123456/ngshare.svg?branch=master
    :target: https://travis-ci.org/lxylxy123456/ngshare

.. image:: https://codecov.io/gh/lxylxy123456/ngshare/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/lxylxy123456/ngshare

.. image:: https://readthedocs.org/projects/ngshare/badge/?version=latest
    :target: https://ngshare.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

``ngshare`` is a backend server for `nbgrader <https://github.com/jupyter/nbgrader>`_'s exchange service.

`nbgrader <https://github.com/jupyter/nbgrader>`_ is a Jupyter notebooks extension for grading running on JupyterHub, but it does not work well in distributed setup of JupyterHub like in Kubernetes, because the file systems exchange uses are not connected between containers. 

To solve this problem, we are letting exchange to gather all information it needs from a set of REST APIs, which is implemented by ``ngshare``.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   user_guide/install.rst
   user_guide/uninstall.rst
   user_guide/extra.rst
   user_guide/notes.rst
   user_guide/bugs.rst

.. toctree::
   :maxdepth: 2
   :caption: APIs

   api/index.rst
   api/definition.rst
   api/req_res.rst
   api/authentication.rst
   api/course.rst
   api/assignment.rst

.. toctree::
   :maxdepth: 2
   :caption: Contributor Guide

   contributer_guide/why_ngshare.rst
   contributer_guide/dev_history.rst
   contributer_guide/system_architecture.rst
   contributer_guide/project_structure.rst
   contributer_guide/decisions.rst
   contributer_guide/install.rst
   contributer_guide/vngshare.rst
   contributer_guide/development.rst
   contributer_guide/database.rst
   contributer_guide/alembic.rst
   contributer_guide/docs.rst
   contributer_guide/deploy.rst

