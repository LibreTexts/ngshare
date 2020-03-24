# ngshare
`ngshare` is the final API server that will be used in nbgrader in production.
 Written as Tornado Web Server and using SQLAlchemy.

## Setup
Document for setting up ngshare is in [/testing](/testing#testing-setup)

### vngshare setup
vngshare stands for Vserver-like Notebook Grader Share. It is similar to vserver
 and allows easy testing.
1. `pip3 install tornado jupyterhub sqlalchemy`
2. `cd ngshare`
3. `python3 vngshare.py [bind_IP_address [port_number]]`
4. Note that `/tmp/ngshare.db` will be the database created
5. Though there is no file system APIs, so your system should be safe, but
 unauthorized people can corrupt your data.
6. To test, when `vngshare.py` is running with default IP and port,
 `pytest test_ngshare.py`

