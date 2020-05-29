Notes for Administrators
========================
Make sure to completely read and understand the following before putting ``ngshare`` into production.

Admin users
-----------
Admin users are the only users who can create courses and assign instructors to them. This is to prevent unauthorized users from creating courses. All admins have full access to every course on ``ngshare``, so keep this in mind when assigning admins. Courses can be created and managed using the `ngshare-course-management <course_management.html>`_ tool that comes with ``ngshare_exchange``.

Race Condition
--------------
ngshare should NOT be run concurrently, or there may be race conditions and data may be corrupted. For example, do not create multiple ngshare instances that share the same underlying database.

Database Upgrade
----------------
ngshare checks the database version every time it starts up. If the database version is older than the ngshare version, it performs schema and data migration. 

Under normal circumstances, migrations only happen after ngshare is updated and the update involves changing the database structure. The ngshare database update log can be found in :doc:`/contributer_guide/alembic`.

The check can be disabled using the command line argument ``--no-upgrade-db`` or the helm chart value ``ngshare.upgrade_db: false``, but do not disable it unless you have a good reason and know the possible consequences.

Database Backup
---------------
ngshare users should regularly back up the database in case of corruption.

The database should be backed up before updating ngshare because the schema and data migration may corrupt the database.

Removing Semantics
------------------
Removing something (e.g. assignment, course) in ngshare will remove relevant objects and relations in database, but the actual files are NOT removed from the storage path.

If storage space is a problem, the administrators can dump the database and remove files from the file system that are not referenced by the database.

Internal Server Error
---------------------
Users may receive 500 Internal Server Error in some extreme cases, for example:

* Database or storage path has incorrect permission, or disk is full.
* There are too many files (probably more than :math:`10^{18}`) created and
  causes Version 4 UUID collision in ``json_files_unpack()``.

Limitations
-----------
* ngshare cannot run concurrently, which may be a bottle neck if too many users
  are using this service.
* ngshare stores all uploaded files in a same directory. This may create
  performance issues when there are too many files uploaded.
* Currently there are no control on user uploads (e.g. file size, number of
  files).
* Admin user names cannot contain "," (comma sign).
* User names are not designed to be changable.

