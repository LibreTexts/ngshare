Course Management
=================

To manage students in your course, please don't use formgrader's web interface since it doesn't use ngshare. Instead, use the ``ngshare-course-management`` command that gets installed with ``ngshare_exchange``. You can use ``ngshare-course-management -h`` to view the help message, and ``ngshare-course-management subcommand -h`` to view details on how to use the subcommand.

Admin Only Commands
-------------------

Creating Courses
^^^^^^^^^^^^^^^^

To create a course, run ``ngshare-course-management create_course COURSE_ID [INSTRUCTOR [INSTRUCTOR ...]]``. ``COURSE_ID`` is the ID of the course created, and you may specify a list of instructors that are added to the course. If you leave this empty, the course won't have any instructors and you may add them later.

Adding/Updating Instructors
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add an instructor to a course, run ``ngshare-course-management add_instructor COURSE_ID INSTRUCTOR_ID``. The ID is the instructor's JupyterHub username. You may also specify ``-f FIRST_NAME``, ``-l LAST_NAME``, and ``-e EMAIL`` for the instructor. If the instructor already exists, their name and email will be updated.

Removing Instructors
^^^^^^^^^^^^^^^^^^^^

To remove an instructor from a course, run ``ngshare-course-management remove_instructor COURSE_ID INSTRUCTOR_ID``. This will revoke their access to the specified course.

Instructor Commands
-------------------

Adding a Single Student
^^^^^^^^^^^^^^^^^^^^^^^

To add a student to a course, run ``ngshare-course-management add_student COURSE_ID STUDENT_ID``. This will add the student to both ngshare and the local nbgrader gradebook. The ID is the student's JupyterHub username. You may also specify ``-f FIRST_NAME``, ``-l LAST_NAME``, and ``-e EMAIL`` for the student. If the student already exists, their name and email will be updated. If you do not want to add the student to the local nbgrader gradebook, you can specify ``--no-gb``.

Adding Students in Bulk
^^^^^^^^^^^^^^^^^^^^^^^

To add multiple students at once, create a CSV file with the following contents:

.. code::

    student_id,first_name,last_name,email
    sid1,jane,doe,jd@mail.com
    sid2,john,perez,jp@mail.com

The header must be ``student_id,first_name,last_name,email``. After that, enter students one line at a time. You may omit the first name, last name and/or email if needed, but there should be 3 commas per line (for example, ``student,,,`` is a student with no name or email).

After you create the CSV file, run ``ngshare-course-management add_students COURSE_ID PATH_TO_CSV_FILE``. This will also add students to the local nbgrader gradebook. If you do not want this to happen (only add students to ngshare, not the gradebook), you can specify ``--no-gb``.

Removing Students
^^^^^^^^^^^^^^^^^

To remove students from a course, run ``ngshare-course-management remove_students COURSE_ID STUDENT [STUDENT ...]``. You can specify multiple students in the same command. This will remove students from both ngshare and the local nbgrader gradebook. If you do not want to remove students from the local gradebook, use ``--no-gb``. If you want to force removal of a student from the local gradebook (even if this deletes their grades), use ``--force``.
