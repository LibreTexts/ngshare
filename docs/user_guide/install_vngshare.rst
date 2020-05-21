vngshare
========

vngshare stands for Vserver-like Notebook Grader Share. It is similar to `vserver <https://github.com/lxylxy123456/ngshare-vserver/>`_ and allows easy testing.

1. Install dependencies. ``pip3 install tornado jupyterhub sqlalchemy``
2. ``cd ngshare``
3. Run vngshare. ``python3 vngshare.py [--host <bind_IP_address> [--port <port_number>]]``

vngshare will create a database at ``/tmp/ngshare.db``. Though there is no file system API, unauthorized users can corrupt your data. You can test vngshare by running it with the default IP and port and executing ``pytest test_ngshare.py``.

