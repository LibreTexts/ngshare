Decisions
=========

Race Condition
--------------
It is possible to configure multiple ``ngshare`` instances to run at the same time, or allow one ``ngshare`` instance to run in multithread mode. This may trigger an untested race condition and cause an error in production.

We decided to warn users about this when they try to configure ``ngshare`` in this way.

Database Update
---------------
There are a few options on letting whom to update the database:

1. Users must manually use `alembic upgrade head` when ngshare updates,
   otherwise ngshare will refuse to start.
2. ngshare will automatically run alembic upgrade on startup, but the user can
   choose to turn this off using a command line argument.
3. ngshare will automatically run alembic upgrade on startup. The user may not
   disable this.

JupyterHub is using option 2, and we decide to follow this, so that users do not have to perform manual intervention during upgrades. So it is developers' responsibility to make sure Alembic upgrade will not break (e.g. write enough test cases).

To make sure users do not encounter database version problems, we decided to automatically run Alembic upgrade (both schematic and data migration) each time ngshare / vngshare is started. There is little overhead for the version check. We assume that users are regularly backing up their database (e.g. when data migration fails, the database's schema may be updated while ``alembic_version`` is not).
