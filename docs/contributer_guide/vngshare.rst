vngshare
========
vngshare is the stand-alone mode version of ngshare. It stands for Vserver-like Notebook Grader Share. It is similar to `vserver <https://github.com/lxylxy123456/ngshare-vserver/>`_ and allows easy testing.

vngshare by default enables debug (e.g. verbose error output). It allows developers to view and reset database content easily. Users can be authenticated by just passing the username in GET / POST requests (see :doc:`/api/authentication`).

To install ``vngshare``:

1. Install dependencies. ``pip3 install tornado jupyterhub sqlalchemy``
2. ``cd ngshare``
3. Run vngshare. ``python3 vngshare.py [--host <bind_IP_address> [--port <port_number>]]``

vngshare will create a database at ``/tmp/ngshare.db`` and store uploaded files in ``/tmp/ngshare/``. Though there is no file system APIs like in vserver, unauthorized users can easily corrupt your data. So do not use in production.

