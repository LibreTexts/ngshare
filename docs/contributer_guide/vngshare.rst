vngshare
========
vngshare is the stand-alone mode of ngshare. It stands for Vserver-like Notebook Grader Share. It is similar to `vserver <https://github.com/lxylxy123456/ngshare-vserver/>`_ and allows easy testing. For details about vserver, see "Development History" below.

Install
-------
For detailed instructions, see :doc:`install`.

.. code:: bash

    pip3 install tornado jupyterhub sqlalchemy
    cd ngshare
    python3 vngshare.py [--host <bind_IP_address> [--port <port_number>]]

Default Behavior
----------------

vngshare by default enables debug (e.g. verbose error output). It allows developers to view and reset database content easily. Users can be authenticated by simply passing in their username in GET / POST requests (see :doc:`/api/authentication`).

vngshare will create a database at ``/tmp/ngshare.db`` and store uploaded files in ``/tmp/ngshare/``. Though there is no file system APIs like in vserver, unauthorized users can easily corrupt your data. So do not use in production.

Development History
-------------------

The development of ``ngshare`` (backend) requires collaborating with frontend development and requires solving technical issues, so our plan breaks the development into different stages.

1. Develop ``vserver`` (see :doc:`project_structure`) with Unix file system APIs.
   This allows frontend to forward all file system calls (e.g. read file, write
   file) to another server. It allows frontend to test the idea when backend is
   implementing next stage.

2. Develop ``vserver`` with nbgrader APIs (e.g. create course, release assignment).
   After this the frontend can begin large changes to the exchange mechanism
   by replacing file system calls with nbgrader API calls. At this point no
   authentication is made.

3. Add authentication to ``vserver`` nbgrader APIs. To make things simple the
   frontend just needs to send the username, and the backend trusts what frontend
   does. During the first three stages, the backend can concurrently investigate
   how to set up a JupyterHub service.

4. Port ``vserver``'s nbgrader APIs to ``ngshare`` (final API server). There should be
   minimal effort in both backend and frontend as long as JupyterHub service can
   be set up correctly. The front end need to change the address of the server
   and send an API token instead of username; the backend need to copy the logic
   of ``vserver``.

5. Maintain ``ngshare``, fix any bugs and implement any features as frontend
   requests.

Currently we are at stage 5. 

Historical Project Structure
----------------------------

This project used to has 2 parts

* ``ngshare`` is the final API server that will be used in nbgrader in production.
  Written as Tornado Web Server and using SQLAlchemy.

  * ``vngshare`` stands for Vserver-like Notebook Grader Share. It has the same
    functionality as ``ngshare`` but is built as a stand-alone server (does not
    require JupyterHub environment), which makes testing easier.

* ``vserver`` is a simple and **vulnerable** API server, written in Flask, that
  allows testing the project structurte and development of frontend without
  waiting for backend.

  * Mar 7, 2020: Since ``ngshare`` is already mature, ``vserver`` is no longer
    maintained.

  * May 9, 2020: ``vserver`` is migrated to
    `https://github.com/lxylxy123456/ngshare-vserver/
    <https://github.com/lxylxy123456/ngshare-vserver/>`_

