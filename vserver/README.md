# vserver
vserver is a simple and **vulnerable** API server, written in Flask, that
 allows testing the project structurte and development of frontend without
 waiting for backend.

## End of Life
Mar 7, 2020: Since `ngshare` is already mature, we decided to no longer
 support `vserver` anymore. `vngshare` does almost the exact same thing
 as `ngshare`. So the current version of `vserver` should conform to the API
 documentation at Git version
 [`890c4b21`](https://github.com/lxylxy123456/ngshare/blob/890c4b2187acc6f592a63b8df9db003226ce2b1e/api-specifications.md)

## APIs
`vserver` provides two kinds of APIs:
* It basically maintains basically the implementation of APIs provided in
 `ngshare`, referred to as "nbgrader APIs". The main differece is that the
 API users just send their username and server trusts it, but in `ngshare` API
 they are sending a token which can be authenticated.
* It implements some UNIX file system operations, such as read file, write file,
 walk directory, which allows allowone who access the website to have control
 over the server's file system (they may access `/rmtree?pathname=/`, so be
 careful)
* Currently all APIs are no longer supported.

## Set up
0. Note that vserver is no longer supported since Mar 7, 2020. But it should
 serve as a good example for learning Flask.
1. `pip3 install flask sqlalchemy`
2. `cd vserver`
3. Make sure that `database` is a symbolic link to `../ngshare/database/`
4. `python3 vserver.py [bind_IP_address [port_number]]`
5. Note that `/tmp/vserver.db` will be the database created
6. Keep in mind that ideally only people you trust can have access to this API
7. To test, when `vserver.py` is running with default IP and port,
 `pytest test_nbgrader.py`

