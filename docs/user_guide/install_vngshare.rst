Install vngshare
================

vngshare stands for Vserver-like Notebook Grader Share. It is similar to `vserver <https://github.com/lxylxy123456/ngshare-vserver/>`_ and allows easy testing.

1. ``pip3 install tornado jupyterhub sqlalchemy``
2. ``cd ngshare``
3. ``python3 vngshare.py [bind_IP_address [port_number]]``
4. Note that ``/tmp/ngshare.db`` will be the database created
5. Though there is no file system APIs, so your system should be safe, but
   unauthorized people can corrupt your data.
6. To test, when ``vngshare.py`` is running with default IP and port,
   ``pytest test_ngshare.py``

