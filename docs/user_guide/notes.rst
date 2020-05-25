Notes for Administrators
========================
Make sure to completely read and understand the following before putting ``ngshare`` into production

Race Condition
--------------
ngshare should NOT run concurrently, or there may be race conditions and data may be corrupted. For example, do not create multiple ngshare instances that share a same underlying database.

Database Upgrade
----------------
ngshare checks database version every time it starts up. If database version is older than ngshare version, it performs schema and data migration. Normally this may only happen after ngshare is updated.

The check can be disabled using ``--no-upgrade-db`` but do not disable it unless you have a good reason and know the possible consequences. 

The database update history can be found in :doc:`/contributer_guide/alembic`.

Database Backup
---------------
ngshare users should regularly backup the database. Especially the database should be backed up before updating ngshare. Because after the update, the schema and data migration may corrupt the database.

Removing Semantics
------------------
Removing something (e.g. assignment, course) in ngshare will remove relevant objects and relations in database, but the actual files are NOT removed from the storage path.

If storage space is a problem, the administrators can dump the database and remove files from the file system that are not referenced by the database.

