Installing on a Z2JH cluster
============================

This guide assumes you are already familiar with installing Z2JH. You should also be familiar with using Helm.

If you prefer looking at examples instead, `here's <https://github.com/lxylxy123456/ngshare/testing/install_z2jh>`_ a sample installation setup. It doesn't demonstrate all the configurable options, though.

Installing ngshare
------------------

Installing the helm chart
^^^^^^^^^^^^^^^^^^^^^^^^^

``ngshare`` is prepackaged into a Helm chart. You may add the repo like this:

.. code:: bash

    helm repo add ngshare https://rkevin-arch.github.io/ngshare-helm-repo/
    helm repo update

Afterwards, create a ``config.yaml`` file to customize your helm chart. Here's a bare minimum ``config.yaml`` file:

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
      admins:
        - admin1
        - admin2

    pvc:
      # Amount of storage to allocate
      storage: 1Gi

For a full list of configurable values, check `here <https://github.com/lxylxy123456/ngshare/blob/master/helmchart/ngshare/values.yaml>`_.

You can now install ``ngshare`` using Helm:

.. code:: bash

    # For helm3
    helm install ngshare ngshare/ngshare -f config.yaml
    # For helm2
    helm install ngshare/ngshare -n ngshare -f config.yaml

After installation, Helm should give you some instructions on how to configure Z2JH.

Configuring Z2JH to work with ngshare
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
            'url': 'http://ngshare:8080',
            'api_token': 'demo_token_9wRp0h4BLzAnC88jjBfpH0fa4QV9tZNI'})

If you have installed ``ngshare`` in the same namespace as JupyterHub, then just add this to your Z2JH ``config.yaml``. Otherwise, you will have to change the URL and use the fully qualified domain name for the ``ngshare`` service (usually ``ngshare.my-namespace.svc.cluster-domain.example``). After you have updated Z2JH's configuration using ``helm upgrade``, you can verify the service is working as intended by logging into JupyterHub, clicking "Control Panel", then "Services -> ngshare". If you see the ``ngshare`` welcome page, you may proceed.

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

Finally, you need to configure nbgrader to use ngshare_exchange. This can be done by adding the following to nbgrader's global config file, ``/etc/jupyter/nbgrader_config.py``:

.. code:: python

    from ngshare_exchange import configureExchange
    c=get_config()
    configureExchange(c)
    c.CourseDirectory.course_id = '*'

A sample singleuser Dockerfile that does all of the above is available `on Github <https://github.com/lxylxy123456/ngshare/testing/install_z2jh/Dockerfile-singleuser>`_.

If running ``nbgrader list`` doesn't cause any significant errors, you have installed ``ngshare_exchange`` correctly. Please check `Notes for Administrators <notes_admin.html>`_ and `Notes for Instructors <notes_instructor.html>`_ for more information on how to use ``ngshare``. The students should be able to use nbgrader as normal without additional configuration.