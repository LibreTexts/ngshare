Command Line Arguments
======================

Here's a list of command line arguments you may specify when starting ``ngshare``.

Regular Arguments
-----------------

``--database PATH_TO_DATABASE``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Specify a custom database for SQLAlchemy. Defaults to ``sqlite:////srv/ngshare/ngshare.db``. Note that using other types of databases (such as MySQL) is not tested.

``--storage PATH_TO_STORAGE``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Specify a folder to store user-uploaded files. Defaults to ``/srv/ngshare/files/``.

``--admins ADMIN1,ADMIN2,ADMIN3``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Specify usernames of administrators separated by commas. Administrators may create courses and access any course.


Advanced Arguments
------------------

You should not be using these command-line arguments unless you know what you're doing or have a very specific need (such as running ngshare as an external service).

``--debug``
^^^^^^^^^^^
Enable debug mode. This gives more helpful error messages and enables features like dumping the database. **WARNING:** Enabling this *will* leak private information, do *NOT* turn this on in production.

``--no-upgrade-db``
^^^^^^^^^^^^^^^^^^^
Do not use Alembic to automatically upgrade the ngshare database. This will cause ngshare to break after an update if the database schema has changed. Please check `Notes for Administrators <notes_admin.html#database-upgrade>`_ for more info.

``--jupyterhub_api_url CUSTOM_API_URL``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Override the JupyterHub API URL configured using the ``JUPUTERHUB_API_URL`` environment variable. You should only use this if you're installing ``ngshare`` as an unmanaged service.

``--prefix PREFIX``
^^^^^^^^^^^^^^^^^^^
Override the default URL prefix configured using the ``JUPYTERHUB_SERVICE_PREFIX`` environment variable. Override the JupyterHub API URL configured using the ``JUPUTERHUB_API_URL`` environment variable. You should only use this if you're installing ``ngshare`` as an unmanaged service.

``--vngshare``
^^^^^^^^^^^^^^
Enable `vngshare mode <extra.html#vngshare>`_. Do not use in production.

``--host BIND_HOST`` and ``--port BIND_PORT``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Specify the host and port to bind to *in vngshare mode only*. To change the port ngshare binds to, please `change <install_unmanaged.html>`_ the ``$JUPYTERHUB_SERVICE_URL`` environment variable instead.
