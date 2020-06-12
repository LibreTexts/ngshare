Intalling in a Regular JupyterHub Environment as a Managed Service
==================================================================

This guide assumes you already know how to set up a JupyterHub environment. You should also be familiar with `adding JupyterHub-managed services <https://jupyterhub.readthedocs.io/en/stable/reference/services.html#hub-managed-services>`_ into ``jupyterhub_config.py``.

If you prefer looking at examples instead, `here's <https://github.com/LibreTexts/ngshare/tree/master/testing/install_jhmanaged>`_ a sample installation setup. It doesn't demonstrate all the configurable options, though.

Installing ngshare
------------------

First, you should install ``ngshare`` in the same environment as the hub.

.. code:: bash

    python3 -m pip install ngshare

After it's installed, you should tell JupyterHub to spawn ``ngshare`` as a managed service on startup. This can be done using something like this inside ``jupyterhub_config.py``:

.. code:: python

    c.JupyterHub.services.append(
        {
            'name': 'ngshare',
            'url': 'http://127.0.0.1:10101',
            'command': ['python3', '-m', 'ngshare', '--admins', 'admin,admin2'],
        }
    )

You may want to check the `list of command line arguments <cmdline.html>`_ for further configuration. JupyterHub will automatically spawn ``ngshare`` on port 10101 in this case.

After you restart JupyterHub, you can verify the service is working as intended by logging into JupyterHub, clicking "Control Panel", then "Services -> ngshare". If you see the ``ngshare`` welcome page, you may proceed.

Installing ngshare_exchange
---------------------------

``ngshare_exchange`` only works with nbgrader version 0.7.0 or above. Unfortunately, that version is not yet released. You will have to install the latest nbgrader from GitHub first:

.. code:: bash

    python3 -m pip install git+https://github.com/jupyter/nbgrader.git@5a81fd5
    jupyter nbextension install --symlink --sys-prefix --py nbgrader
    jupyter nbextension enable --sys-prefix --py nbgrader
    jupyter serverextension enable --sys-prefix --py nbgrader

Afterwards, you may install ``ngshare_exchange``:

.. code:: bash

    python3 -m pip install ngshare_exchange

Finally, you need to configure nbgrader to use ngshare_exchange. This can be done by adding the following to nbgrader's global config file, ``/etc/jupyter/nbgrader_config.py``:

.. code:: python

    from ngshare_exchange import configureExchange
    c=get_config()
    # Note: It's important to specify the right ngshare URL when not using k8s
    configureExchange(c, 'http://127.0.0.1:10101/services/ngshare')

    # Add the following to let students access courses without configuration
    # For more information, read Notes for Instructors in the documentation
    c.CourseDirectory.course_id = '*'

You will have to specify the right URL to ngshare inside ``configureExchange``. This is usually ``http://ip:port/services/ngshare`` where ``ip`` is the hub's IP and ``port`` is the port ngshare runs on. Make sure each user can access this endpoint.

If running ``nbgrader list`` doesn't cause any significant errors, you have installed ``ngshare_exchange`` correctly. Please check `Notes for Administrators <notes_admin.html>`_ and `Notes for Instructors <notes_instructor.html>`_ for more information on how to use ``ngshare``. The students should be able to use nbgrader as normal without additional configuration.
