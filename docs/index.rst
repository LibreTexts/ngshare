ngshare
=======
``ngshare`` is a backend server for `nbgrader <https://github.com/jupyter/nbgrader>`_'s exchange service.

.. image:: assets/favicon.svg
    :width: 64
    :alt: ngshare Logo

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://travis-ci.org/LibreTexts/ngshare.svg?branch=master
    :target: https://travis-ci.org/LibreTexts/ngshare

.. image:: https://codecov.io/gh/LibreTexts/ngshare/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/LibreTexts/ngshare

.. image:: https://readthedocs.org/projects/ngshare/badge/?version=latest
    :target: https://ngshare.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

`nbgrader <https://github.com/jupyter/nbgrader>`_ is a Jupyter notebooks extension for grading running on JupyterHub, but it does not work well in distributed setup of JupyterHub like in Kubernetes, because the file systems exchange uses are not connected between containers. 

To solve this problem, we are letting exchange to gather all information it needs from a set of REST APIs, which is implemented by ``ngshare``.

Project Introduction Video
--------------------------

.. raw:: html

    <p><iframe width="640" height="360" src="https://www.youtube.com/embed/FdK0AGwxkSw" frameborder="0" allowfullscreen></iframe></p>

Youtube Video Demo
------------------

.. raw:: html

    <p><iframe width="640" height="360" src="https://www.youtube.com/embed/SEJCaqD7xXQ" frameborder="0" allowfullscreen></iframe></p>

Table of Contents
-----------------

.. toctree::
   :maxdepth: 3
   :caption: User Documentation

   user_guide/install.rst
   user_guide/uninstall.rst
   user_guide/upgrade.rst
   user_guide/cmdline.rst
   user_guide/extra.rst
   user_guide/notes_admin.rst
   user_guide/notes_instructor.rst
   user_guide/course_management.rst
   user_guide/bugs.rst
   user_guide/change_log.rst

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

