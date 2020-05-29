Extra Features
==============

Welcome Page
------------
``GET /api/``

A welcome page for the API, containing some sample uses of the API.

If you are an admin user or ngshare / vngshare is running in debug mode, you can see "Debug actions" (explained below).

Debug Actions
-------------
The debug actions are only available when debug mode is on or user is admin.

Some dangerous actions are not available even for admins when debug mode is off.

Dump Database
^^^^^^^^^^^^^
``GET /api/initialize-Data6ase?action=dump``

Dump the database content in JSON format.

Human Readable Format
"""""""""""""""""""""
``GET /api/initialize-Data6ase?action=dump&human-readable=true&user=root``

Dump the database content in human readable format. (Displayed with the help of `Masonry.js <https://masonry.desandro.com/>`_)

Clear Database
^^^^^^^^^^^^^^
``GET /api/initialize-Data6ase?action=clear``

Remove the entire content of database (the currently logged-in user cannot be removed). Only available when debug mode is on.

Initialize with Test Data
^^^^^^^^^^^^^^^^^^^^^^^^^
``GET /api/initialize-Data6ase?action=init``

Initialize database with some pre-defined test data. Only available when debug mode is on.

Health Endpoint
---------------
``GET /healthz``

This always returns a single JSON object with ``{"success": true}``. It can be used as a liveness probe to ensure ngshare is up and running.

vngshare
--------

vngshare stands for Vserver-like Notebook Grader Share. It is similar to `vserver <https://github.com/lxylxy123456/ngshare-vserver/>`_ and allows easy testing.

To run vngshare, do the following:

1. Install dependencies. ``pip3 install tornado jupyterhub sqlalchemy``
2. ``cd ngshare``
3. Run vngshare. ``python3 vngshare.py [--host <bind_IP_address> [--port <port_number>]]``

vngshare will create a database at ``/tmp/ngshare.db``. Though there is no file system API, unauthorized users can corrupt your data. You can test vngshare by running it with the default IP and port and executing ``pytest test_ngshare.py``.
