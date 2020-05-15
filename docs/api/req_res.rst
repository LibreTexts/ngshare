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

Response
--------
When the client is not authenticated (e.g. not logged in), server will return HTTP 301 and redirect user to log in page

When the client tries to access an invalid entrypoint, server will return HTTP 404 Not Found

When the client performs a request with an invalid method, server will return HTTP 405 Method Not Allowed

When the client is authenticated, server will return a status code and a JSON object (specified below).

* When success, the status code will be 200 and response will be
  ``{"success": true, ...}``, where ``...`` may contain extra information.

* When fail, the status code will be between 400 and 499 (inclusive). The
  response will be ``{"success": false, "message": "Error Message"}``.
  Possible values for ``Error Message`` are defined in each "Error messages"
  sections.

* When server encounters an error, it will return 500. In this case, the client
  should submit a bug report and report this to ngshare maintainers.

