Definitions
===========

Admin User
----------
Admin users have special privilege on ngshare (e.g. create / delete courses). The list of admin users can be set by ``--admins=`` argument in ngshare or vngshare.

Assignment Name
---------------
Also referred to as ``assignment_id``, this is a unique name for an assignment within a course. For example, "Assignment 1".

Checksum
--------
The md5 checksum of a file.

Course Name
-----------
Also referred to as ``course_id``, this is a unique name for a course. For example, "NBG 101".

Directory Tree
--------------
Assignments consist of a directory, notebook files in the root, and optional supplementary files in the root and/or subdirectories. In order to send an entire assignment in one request, a JSON file has a list of maps for each file. The following structure will be referred to as "encoded directory tree."

``path`` should be in Unix style, and should be relative. For example: ``a.ipynb`` or ``notes/a.txt``. Pathnames not following this style will be rejected by server with error 400 "Illegal path".

.. code:: javascript

    [
        {
            "path": /* file path relative to the root */,
            "content": /* base64 encoded file contents */,
            "checksum": /* md5 checksum of file contents */
        },
        ...
    ]

Instructor ID
-------------
The ID given to an instructor. For example, "course1_instructor" or "doe_jane".

Notebook Name
-------------
Also referred to as ``notebook_id``, this is the base name of a .ipynb notebook without the extension. For example, "Problem 1" is the name for the notebook "Problem 1.ipynb".

Student ID
----------
The ID given to a student. For example, "doe_jane".

Timestamp
---------
A timestamp of when a user initiates the assignment submission process. It follows the `format <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_ ``"%Y-%m-%d %H:%M:%S.%f %Z"``. For example, ``2020-01-30 10:30:47.524219 UTC``.

