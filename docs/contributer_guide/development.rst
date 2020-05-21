Development
===========

Testing
-------
.. code:: bash

    pip3 install pytest pytest-cov pytest-tornado
    cd ngshare
    pytest

Coverage
^^^^^^^^
.. code:: bash

    pytest --cov=.

Show uncovered lines

.. code:: bash

    pytest --cov-report term-missing --cov=. .

Code Formatting
---------------
.. code:: bash

    pip3 install black
    black -S -l 80 .

