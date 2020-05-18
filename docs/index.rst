ngshare
=======

``ngshare`` is a backend server for `nbgrader <https://github.com/jupyter/nbgrader>`_'s exchange service.

`nbgrader <https://github.com/jupyter/nbgrader>`_ is a Jupyter notebooks extension for grading running on JupyterHub, but it does not work well in distributed setup of JupyterHub like in Kubernetes, because the file systems exchange uses are not connected between containers. 

To solve this problem, we are letting exchange to gather all information it needs from a set of REST APIs, which is implemented by ``ngshare``.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   user_guide/install_ngshare.rst
   user_guide/install_vngshare.rst
   user_guide/extra.rst

.. toctree::
   :maxdepth: 3
   :caption: APIs

   api/index.rst

.. toctree::
   :maxdepth: 2
   :caption: Contributor Guide

   contributer_guide/why_ngshare.rst
   contributer_guide/dev_history.rst
   contributer_guide/project_structure.rst
   contributer_guide/decisions.rst
   contributer_guide/development.rst
   contributer_guide/database.rst
   contributer_guide/alembic.rst
   contributer_guide/docs.rst

