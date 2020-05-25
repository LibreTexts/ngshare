vngshare
========
vngshare is the stand-alone mode version of ngshare. It stands for Vserver-like Notebook Grader Share. It is similar to `vserver <https://github.com/lxylxy123456/ngshare-vserver/>`_ and allows easy testing.

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
