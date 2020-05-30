Frequently Asked Questions
==========================

Do I need to backup database?
-----------------------------
Yes, you should regularly backup your database in case of corruption. 

The database should be backed up before updating ngshare because the schema and data migration may corrupt the database.

See :doc:`notes_admin` for details.

Will attackers be able to clear ngshare database?
-------------------------------------------------
Though there is a "clear database" button in ngshare welcome page, this functionality is disabled as long as you are not starting ngshare in debug mode (which is the default configuration for ngshare). So attackers cannot directly clear your database even if they log in as an admin user in ngshare. 

