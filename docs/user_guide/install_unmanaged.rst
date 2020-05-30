Intalling as an Unmanaged Service
=================================

**WARNING:** This is for advanced configurations only. Unless you wish to run ``ngshare`` in a different environment than the hub, or have very specific proxying setups, you should not be using this guide.

This guide assumes you already have a JupyterHub environment setup. You will need to manage ``ngshare`` separately as a service, and ensure it and the hub can communicate with one another.

Installing ngshare
------------------

Mocking Required Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``ngshare`` gets some configurations from the hub via `environment variables <https://jupyterhub.readthedocs.io/en/stable/reference/services.html#launching-a-hub-managed-service>`_. To run ``ngshare``, you will need to mock these variables. You should at least set the following:

``JUPYTERHUB_API_TOKEN`` should be a unique, secret token (such as one generated using ``openssl rand -hex 32``). This should be the same token specified in JupyterHub's config.

``JUPYTERHUB_API_URL`` should point to the hub API, such as ``http://127.0.0.1:8080/hub/api``. Make sure this endpoint is accessible to ``ngshare``.

``JUPYTERHUB_SERVICE_PREFIX`` is the prefix under which ``ngshare`` operates, with a leading and trailing slash. JupyterHub will proxy requests from ``/services/your-service-name/``, so this is usually ``/services/ngshare/`` if the service name is ``ngshare``.

``JUPYTERHUB_SERVICE_URL`` is the URL that ``ngshare`` should be accessible on. For example, if ``ngshare`` has IP ``10.1.2.3`` and you want ``ngshare`` to listen on port 1234, this should be ``http://10.1.2.3:1234``. Changing this will affect ``ngshare``'s port.

Running ``ngshare``
^^^^^^^^^^^^^^^^^^^
After configuring the environment variables, you may start ngshare as a service. You should also take a look at the `list of command line arguments <cmdline.html>`_ for further configuration.

Configuring JupyterHub
^^^^^^^^^^^^^^^^^^^^^^
Inside JupyterHub's configuration Python script, add the following:

.. code:: python

    c.JupyterHub.services.append(
        {
            'name': 'ngshare',
            'url': 'http://ngshare-location:1234',
            'api_token': 'top-secret-api-token',
        }
    )

Make sure the ``url`` field points to ngshare, and the ``api_token`` is the same one specified as an environment variable to ``ngshare``.

After you restart JupyterHub, you can verify the service is working as intended by logging into JupyterHub, clicking "Control Panel", then "Services -> ngshare". If you see the ``ngshare`` welcome page, you may proceed.

Installing ngshare_exchange
---------------------------

This will be largely the same as `installing ngshare as a managed service <install_jupyterhub.html>`_. You only need to ensure the ngshare URL in ``nbgrader_config.py`` is accessible by the spawned notebook servers.
