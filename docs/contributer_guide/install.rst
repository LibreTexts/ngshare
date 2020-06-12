Developer Installation
======================

For using ``ngshare``, see :doc:`../user_guide/install`.

Install from GitHub
-------------------
.. code:: bash

    git clone https://github.com/LibreTexts/ngshare.git
    cd ngshare/
    pip3 install .

Run Installed ngshare
---------------------
.. code:: bash

    python3 -m ngshare [arguments]

Run ngshare without Installation
--------------------------------
The first line installs pip dependencies.

.. code:: bash

    pip3 install tornado jupyterhub sqlalchemy
    git clone https://github.com/LibreTexts/ngshare.git
    cd ngshare/ngshare/
    python3 ngshare.py [arguments]

Run vngshare
------------
vnshare can be used by running ``vngshare.py`` or by adding some arguments to ngshare.

* ``--vngshare``: Mock authentication (using only username)
* ``--debug``: enable debug
* ``--database sqlite:////tmp/ngshare.db``: change default database path
* ``--storage /tmp/ngshare``: change default storage path

Run vngshare from Installed ngshare
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: bash

    python3 -m ngshare --vngshare --debug [arguments]

Run vngshare without Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: bash

    pip3 install pytest pytest-cov pytest-tornado
    git clone https://github.com/LibreTexts/ngshare.git
    cd ngshare/ngshare/
    python3 vngshare.py [arguments]
    # OR
    python3 ngshare.py --vngshare --debug [arguments]
