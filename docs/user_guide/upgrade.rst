Upgrading
=========

Upgrading ngshare
-----------------
If you installed ngshare using a helm chart, upgrading is as simple as a `helm upgrade`:

.. code:: bash

    helm repo update
    # assuming your release is called ngshare
    helm upgrade ngshare ngshare/ngshare -f your_config.yaml

Please note that if during your first installation you didn't specify an API token, the randomized API token will be regenerated every upgrade. Therefore, it's highly recommended to specify the API token in your config.yaml.

If you aren't using the helm chart and installed ngshare using pip, upgrade through pip:

.. code:: bash

    pip install -U ngshare

Please back up the database before an update just in case. Read `Notes for Administrators <notes_admin.html>`_ for more information on how ngshare upgrades affect the database.

Upgrading ngshare_exchange
--------------------------
ngshare_exchange should be installed as a pip package, so update is simple:

.. code:: bash

    pip install -U ngshare_exchange

No further reconfiguration should be required, although it is recommended to restart all notebook servers after an update.
