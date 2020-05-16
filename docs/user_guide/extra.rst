Extra features
==============

Welcome page
------------
``GET /api/``

A welcome page for the API, containing some sample uses of the API

If you are an admin user or ngshare / vngshare is running in debug mode, you can see "Debug actions" (explained below).

Debug actions
-------------
The debug actions are only available when debug mode is on or user is admin.

Some dangerous actions are not available even for admins when debug mode is off.

Dump database
^^^^^^^^^^^^^
``GET /api/initialize-Data6ase?action=dump``

Dump the database content in JSON format.

Human readable format
"""""""""""""""""""""
``GET /api/initialize-Data6ase?action=dump&human-readable=true&user=root``

Dump the database content in human readable format. (Displayed with the help of `Masonry.js <https://masonry.desandro.com/>`_)

Clear database
^^^^^^^^^^^^^^
``GET /api/initialize-Data6ase?action=clear``

Remove the entire content of database (the current logged in user may not be able to be removed). Only available when debug mode is on. 

Initialize with test data
^^^^^^^^^^^^^^^^^^^^^^^^^
``GET /api/initialize-Data6ase?action=init``

Initialize database with some pre-defined test data. Only available when debug mode is on. 

