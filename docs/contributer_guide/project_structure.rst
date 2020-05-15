Project Structure
=================

This project has 2 parts

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

The database structure is documented in [ngshare/database](ngshare/database).

