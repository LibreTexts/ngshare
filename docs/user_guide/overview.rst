Project Overview
================

``ngshare`` is a backend server for `nbgrader <https://github.com/jupyter/nbgrader>`_'s exchange service.

.. image:: ../assets/favicon.svg
    :width: 64
    :alt: ngshare Logo

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://travis-ci.org/lxylxy123456/ngshare.svg?branch=master
    :target: https://travis-ci.org/lxylxy123456/ngshare

.. image:: https://codecov.io/gh/lxylxy123456/ngshare/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/lxylxy123456/ngshare

.. image:: https://readthedocs.org/projects/ngshare/badge/?version=latest
    :target: https://ngshare.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

`nbgrader <https://github.com/jupyter/nbgrader>`_ is a Jupyter notebooks extension for grading running on JupyterHub, but it does not work well in distributed setup of JupyterHub like in Kubernetes, because the file systems exchange uses are not connected between containers. 

To solve this problem, we are letting exchange to gather all information it needs from a set of REST APIs, which is implemented by ``ngshare``.

Background
----------
UC Davis JupyterHub will be used for course instruction. Students will be able to complete and submit assignments through JupyterHub and instructors can grade assignments. nbgrader will be used to add such functionality to UC Davis JupyterHub, but there are issues. When JupyterHub is deployed as a Kubernetes cluster, nbgrader is unable to automatically distribute and collect assignments since there isn’t a shared filesystem. Also, nbgrader is not compatible with JupyterLab, an improved version of the Jupyter Notebook frontend.

.. image:: ../assets/architecture5a.svg
    :alt: System Architecture Diagram without ngshare
    :align: center

Goals
-----
* Create a JupyterHub service that allows nbgrader to work on a Kubernetes set up
* Create an nbgrader exchange plugin to enable the use of our service
* Provide good testing coverage of our service and plugin
* Package ngshare for easy installation through pip
* Write clear documentation to facilitate the maintenance of our service by the UC Davis Jupyter Team
* Port nbexchange extensions to JupyterLab

Features
--------
1. Sharing files between different Jupyter Notebook servers without relying on a
   shared file system.
2. Managing courses, instructors, and students for ngshare. 
3. Easy interface for administrators to debug ngshare database. 
4. Open source projects with continuous integration, code coverage, and online
   documentation.

Future Application
------------------
Although this project is specifically built for nbgrader and Kubernetes, it can be ported to other container cluster managers like Docker Swarm and Apache Mesos, or even regular JupyterHub environments. The ngshare part of this project can be used as a template when developing other projects that require specialized sharing between containers. 

