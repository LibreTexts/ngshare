Request and Response Format
===========================

Requests
--------
Clients will send HTTP request to server. Possible methods are:

* GET
* POST
* DELETE

The method to use is specified in each API entry point.

The client may need to supply GET parameters or POST data.

GET Example
^^^^^^^^^^^
(For authentication for vngshare, see :doc:`authentication`)

.. code::

    GET /api/assignment/course1/challenge?list_only=true HTTP/1.1
    Host: my-ngshare-host
    Authorization: token ABCDEFGHIJKLMNOPQRSTUVWXYZ

POST Example
^^^^^^^^^^^^
(For authentication for vngshare, see :doc:`authentication`)

.. code::

    POST /api/students/course2 HTTP/1.1
    Host: my-ngshare-host
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 189
    Authorization: token ABCDEFGHIJKLMNOPQRSTUVWXYZ

    students=%5B%7B%22username%22%3A+%22kevin%22%2C+%22first_name%22%3A+%22kevin_first_name%22%2C+%22last_name%22%3A+%22kevin_last_name%22%2C+%22email%22%3A+%22kevin_email%22%7D%5D

Response
--------
When the client is not authenticated (e.g. not logged in), server will return ``HTTP 301`` and redirect user to login page.

When the client tries to access an invalid entrypoint, server will return ``HTTP 404 Not Found``.

When the client performs a request with an invalid method, server will return ``HTTP 405 Method Not Allowed``.

When the client is authenticated, server will return a status code and a JSON object (specified below).

* When success, the status code will be ``200`` and response will be
  ``{"success": true, ...}``, where ``...`` may contain extra information.

* When fail, the status code will be between ``400`` and ``499`` (inclusive).
  The response will be ``{"success": false, "message": "Error Message"}``.
  Possible values for ``Error Message`` are defined in each "Error messages"
  sections.

* When server encounters an error, it will return ``HTTP 500``. In this case,
  the client should submit a bug report and report this to ngshare maintainers.

Success Example
^^^^^^^^^^^^^^^

.. code::

    HTTP/1.1 200 OK
    Server: TornadoServer/6.0.3
    Content-Type: text/html; charset=UTF-8
    Date: Fri, 15 May 2020 19:46:31 GMT
    Content-Length: 95

    {"success": true, "files": [{"path": "file2", "checksum": "3d2172418ce305c7d16d4b05597c6a59"}]}

Error Example
^^^^^^^^^^^^^

.. code::

    HTTP/1.1 403 Forbidden
    Server: TornadoServer/6.0.3
    Content-Type: text/html; charset=UTF-8
    Date: Fri, 15 May 2020 19:50:05 GMT
    Content-Length: 50

    {"success": false, "message": "Permission denied"}


