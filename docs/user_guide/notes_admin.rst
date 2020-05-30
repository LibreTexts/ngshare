Notes for Administrators
========================
Make sure to completely read and understand the following before putting ``ngshare`` into production.

Admin Users
-----------
Admin users are the only users who can create courses and assign instructors to them. This is to prevent unauthorized users from creating courses. All admins have full access to every course on ``ngshare``, so keep this in mind when assigning admins. Courses can be created and managed using the `ngshare-course-management <course_management.html>`_ tool that comes with ``ngshare_exchange``.

User Name Reuse
---------------
In ngshare, all users (instructors and students) are identified using their username in JupyterHub. They are authenticated using the API token inside their notebook server. Be careful when reusing usernames in JupyterHub, as users with the same name will be identified as the same. We haven't added functionality to rename or delete users in ngshare, so be sure not to delete a user and create a new one with the same name. If you do, you will have to manually edit the ngshare database to remove or rename that user.

Race Condition
--------------
ngshare should NOT be run concurrently, or there may be race conditions and data may be corrupted. For example, do not create multiple ngshare instances that share the same underlying database.

Storage
-------
If you're using the Helm chart, only 1GiB of storage is allocated by default. You may increase this limit by specifying `pvc.storage` in the Helm values. If ngshare returns 500 for requests, lack of storage space could be a reason.

Also, when courses or assignments are deleted, their corresponding files are not automatically deleted. You may want to delete these files to clean up storage. See the Removing Semantics section below for more info.

Database Upgrade
----------------
ngshare checks the database version every time it starts up. If the database version is older than the ngshare version, it performs schema and data migration. 

Under normal circumstances, migrations only happen after ngshare is updated and the update involves changing the database structure. The ngshare database update log can be found in :doc:`/contributer_guide/alembic`.

The check can be disabled using the command line argument ``--no-upgrade-db`` or the helm chart value ``ngshare.upgrade_db: false``, but do not disable it unless you have a good reason and know the possible consequences.

Database Backup
---------------
ngshare users should regularly back up the database in case of corruption.

The database should be backed up before updating ngshare because the schema and data migration may corrupt the database.

When installed using Helm, the database and all uploaded files are stored in a PVC usually called ``ngshare-pvc`` (or ``yourreleasename-pvc``). You can back up everything in that volume.

When installed manually using ``pip``, you should have configured where the database is using command line arguments. If not, the database and all uploaded files should be in ``/srv/ngshare``.

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
* ngshare cannot run concurrently, which may be a bottleneck if too many users
  are using this service.
* ngshare stores all uploaded files in one directory. This may create
  performance issues when there are too many files uploaded.
* Currently, there are no limits on user uploads (e.g. file size, number of
  files).
* Admin user names cannot contain "," (comma sign).
* User names are not designed to be interchangeable between students.
