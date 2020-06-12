Installing on a Z2JH Cluster
============================

This guide assumes you already have a Kubernetes cluster with a persistent volume provisioner (which should be the case if you run Z2JH). You should also be familiar with installing Z2JH and using Helm.

If you prefer looking at examples instead, `here's <https://github.com/LibreTexts/ngshare/tree/master/testing/install_z2jh>`_ a sample installation setup. It doesn't demonstrate all the configurable options, though.

Installing ngshare
------------------

Installing the Helm Chart
^^^^^^^^^^^^^^^^^^^^^^^^^

``ngshare`` is prepackaged into a Helm chart. You may add the repo like this:

.. code:: bash

    helm repo add ngshare https://libretexts.github.io/ngshare-helm-repo/
    helm repo update

Afterwards, create a ``config.yaml`` file to customize your helm chart. Here's a bare minimum ``config.yaml`` file that assumes you're installing ``ngshare`` into the same namespace as Z2JH, and that you only need 1GB of storage in total:

.. code:: yaml

    ngshare:
      hub_api_token: demo_token_9wRp0h4BLzAnC88jjBfpH0fa4QV9tZNI
      admins:
        - admin_username

The API token should be generated randomly and kept secret (if you omit it, one will be automatically generated for you).

Here's a sample ``config.yaml`` file that contains the most commonly used options:

.. code:: yaml

    deployment:
      # Resource limitations for the pod
      resources:
        limits:
          cpu: 100m
          memory: 128Mi
        requests:
          cpu: 100m
          memory: 128Mi

    ngshare:
      hub_api_token: demo_token_9wRp0h4BLzAnC88jjBfpH0fa4QV9tZNI
      # Please change the line below with the namespace your Z2JH helm chart is installed under
      # You can omit this value if you're installing ngshare in the same namespace
      hub_api_url: http://hub.your-z2jh-namespace.svc.cluster.local:8081/hub/api
      admins:
        - admin1
        - admin2

    pvc:
      # Amount of storage to allocate
      storage: 1Gi

For a full list of configurable values, check `here <https://github.com/LibreTexts/ngshare/blob/master/helmchart/ngshare/values.yaml>`_.

You can now install ``ngshare`` using Helm:

.. code:: bash

    # For helm3
    helm install ngshare ngshare/ngshare -f config.yaml
    # For helm2
    helm install ngshare/ngshare -n ngshare -f config.yaml

If you didn't install Z2JH in the default namespace, it is recommended to install ``ngshare`` in the same namespace as Z2JH by specifying ``--namespace your_namespace_name`` in ``helm install``. Note that if you don't put ``ngshare`` and Z2JH in the same namespace, you will have to modify the ``ngshare.hub_api_url`` value in your config to point to ``http://hub.your-z2jh-namespace.svc.cluster.local:8081/hub/api`` instead (replace ``your-z2jh-namespace`` with the namespace where Z2JH is installed).

After installation, Helm should give you some instructions on how to configure Z2JH.

Configuring Z2JH to Work with ngshare
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``ngshare`` Helm chart should output something like this at the end of installation:

.. code::

    Congrats, ngshare should be installed!
    To get started, add the following to your JupyterHub helm chart's values:

    hub:
      extraConfig:
        ngshare.py: |
          c.JupyterHub.services.append({
            'name': 'ngshare',
            'url': 'http://ngshare.default.svc.cluster.local:8080',
            'api_token': '3VEgEzkhFkQsdZNI7zhnyMW6U0a2xsZq'})

Follow the instructions and add the code block to your Z2JH ``config.yaml``. After you have updated Z2JH's configuration using ``helm upgrade``, you can verify the service is working as intended by logging into JupyterHub, clicking "Control Panel", then "Services -> ngshare". If you see the ``ngshare`` welcome page, you may proceed.

Installing ngshare_exchange
---------------------------

You should know how to `customize the user environment using Dockerfiles <https://zero-to-jupyterhub.readthedocs.io/en/latest/customizing/user-environment.html>`_ in Z2JH. For the clients to use ``ngshare``, the exchange must be installed in every user pod.

``ngshare_exchange`` only works with nbgrader version 0.7.0 or above. Unfortunately, that version is not yet released. You will have to install the latest nbgrader from GitHub first:

.. code:: bash

    python3 -m pip install git+https://github.com/jupyter/nbgrader.git@5a81fd5
    jupyter nbextension install --symlink --sys-prefix --py nbgrader
    jupyter nbextension enable --sys-prefix --py nbgrader
    jupyter serverextension enable --sys-prefix --py nbgrader

Afterwards, you may install ``ngshare_exchange``:

.. code:: bash

    python3 -m pip install ngshare_exchange

Finally, you need to configure nbgrader to use ngshare_exchange. This can be done by adding some code to nbgrader's global config file, ``/etc/jupyter/nbgrader_config.py``. The relevant code should be output by the ``helm install`` command earlier when you installed ``ngshare``:

.. code:: python

    from ngshare_exchange import configureExchange
    c=get_config()
    configureExchange(c, 'http://ngshare.default.svc.cluster.local:8080/services/ngshare')
    # Add the following line to let students access courses without configuration
    # For more information, read Notes for Instructors in the documentation
    c.CourseDirectory.course_id = '*'

Depending on your helm values and the namespace you install in, the URL will be different. Be sure to follow the code your ``helm install`` command outputs.

A sample singleuser Dockerfile that does all of the above is available `on Github <https://github.com/LibreTexts/ngshare/tree/master/testing/install_z2jh/Dockerfile-singleuser>`_.

If running ``nbgrader list`` doesn't cause any significant errors, you have installed ``ngshare_exchange`` correctly. Please check `Notes for Administrators <notes_admin.html>`_ and `Notes for Instructors <notes_instructor.html>`_ for more information on how to use ``ngshare``. The students should be able to use nbgrader as normal without additional configuration.
