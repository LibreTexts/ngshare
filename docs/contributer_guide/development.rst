Development
===========

Stand-Alone Mode
----------------
Using ``vngshare`` can make developing easy because developers do not need to worry about authentications etc. See :doc:`vngshare`.

Unit Testing
------------
We use `pytest <https://pypi.org/project/pytest/>`_ for unit tests. The `pytest-tornado <https://pypi.org/project/pytest-tornado/>`_ plugin allows us to test a Tornado server.

.. code:: bash

    pip3 install pytest pytest-cov pytest-tornado
    pytest

Coverage
^^^^^^^^
We use `pytest-cov <https://pypi.org/project/pytest-cov/>`_ to gather code coverage. To collect coverage, use:

.. code:: bash

    pytest --cov=./ngshare/

To show uncovered lines, use:

.. code:: bash

    pytest --cov-report term-missing --cov=./ngshare/ ./ngshare/

Code Formatting
---------------
We use `black <https://github.com/psf/black>`_ to format our code.

.. code:: bash

    pip3 install black
    black -S -l 80 .

Contributing
------------

If you want to contribute to ``ngshare``, submit a pull request to `https://github.com/LibreTexts/ngshare/pulls <https://github.com/LibreTexts/ngshare/pulls>`_.
