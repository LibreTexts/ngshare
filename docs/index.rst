ngshare
=======

`ngshare` is a backend server for
 `nbgrader <https://github.com/jupyter/nbgrader>`_'s exchange service.

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   user_guide/install.rst

.. toctree::
   :maxdepth: 2
   :acption: Contributor Guide

   contributer_guide/decisions.rst

`nbgrader <https://github.com/jupyter/nbgrader>`_ is a Jupyter notebooks
 extension for grading running on JupyterHub, but it does not work well in
 distributed setup of JupyterHub like in Kubernetes, because the file systems
 exchange uses are not connected between containers. 

To solve this problem, we are letting exchange to gather all information it
 needs from a set of REST APIs, which is implemented by `ngshare`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
