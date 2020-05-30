Authentication
==============

ngshare Authentication
----------------------

``ngshare`` uses JupyterHub authentication tokens to authenticate the user. This is usually in the ``JUPYTERHUB_API_TOKEN`` environment variable in each user's notebook servers. ``ngshare`` will use this token to fetch the username of the current user. The username is the only information used to identify the user.

To send the token to ``ngshare``, use the ``Authorization: token`` header in HTTP requests to ``ngshare``.

GET Example
^^^^^^^^^^^

.. code::

    GET /api/assignment/course1/challenge?list_only=true HTTP/1.1
    Host: my-ngshare-host
    Authorization: token ABCDEFGHIJKLMNOPQRSTUVWXYZ

POST Example
^^^^^^^^^^^^

.. code::

    POST /api/students/course2 HTTP/1.1
    Host: my-ngshare-host
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 189
    Authorization: token ABCDEFGHIJKLMNOPQRSTUVWXYZ

    instructors=%5B%22eric%22%5D

vngshare Authentication
-----------------------

For ``vngshare``, there is no password authentication. The username is specified in the GET param or POST data field ``user``.

GET Example
^^^^^^^^^^^

.. code::

    GET /api/assignment/course1/challenge?user=lawrence&list_only=true HTTP/1.1
    Host: 127.0.0.1:12121

Post Example
^^^^^^^^^^^^

.. code::

    POST /api/course/course2 HTTP/1.1
    Host: my-ngshare-host
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 38

    instructors=%5B%22eric%22%5D&user=root
