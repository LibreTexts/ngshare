Authentication
==============

ngshare authentication
----------------------

This section is under construction

For ``ngshare``, use JupyterHub authentication.


vngshare authentication
-----------------------

For ``vngshare``, supply the username to the GET param or POST data ``user``.

GET example
^^^^^^^^^^^

.. code::

    GET /api/assignment/course1/challenge?user=lawrence&list_only=true HTTP/1.1
    Host: 127.0.0.1:12121

Post example
^^^^^^^^^^^^

.. code::

    POST /api/course/course2 HTTP/1.1
    Host: my-ngshare-host
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 38

    instructors=%5B%22eric%22%5D&user=root

