Uninstalling
============

Uninstalling ngshare
--------------------
If you installed ngshare using a helm chart, you can uninstall it there. Assuming your release is called ``ngshare``:

.. code:: bash

    # helm3
    helm uninstall ngshare

    # helm2
    helm delete --purge ngshare

If you installed ngshare manually using pip, you may uninstall it there as well:

.. code:: bash

    pip uninstall ngshare

Afterwards, be sure to also modify your Z2JH helm values or ``jupyterhub_config.py`` and remove ngshare as a service.

Please back up the database and user files before uninstalling, in case you need it. Read `Notes for Administrators <notes_admin.html>`_ for more information.

Uninstalling ngshare_exchange
-----------------------------
You may uninstall ngshare using pip:

.. code:: bash

    pip uninstall ngshare_exchange

Be sure to modify the ``nbgrader_config.py`` file and remove references to ngshare_exchange, so you can continue using nbgrader normally.
