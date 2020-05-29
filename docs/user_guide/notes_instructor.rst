Notes for Instructors
=====================
Make sure to read the following to understand how to manage courses with ``ngshare``.

Course cretation
----------------
Only the administrators can create courses due to security concerns. Please contact your system administrator if you want to create a course. After they assign you as an instructor, you may manage the course roster and add more students to the course yourself.

Managing students
-----------------
Please use the `ngshare-course-management <course_management.html>`_ tool when adding / removing students from a course. **Do not use Formgrader's interface to add students**, since this does not update ngshare.

Configuring formgrader
----------------------
Formgrader does not support multiple classes, so you have to tell it which class you're currently teaching. To do this, create a file called ``nbgrader_config.py`` in your home directory with the following contents:

.. code:: python

    c.CourseDirectory.course_id = 'mycourseid'

Replace ``mycourseid`` with the ID of the course you want to view. Afterwards, restart the notebook server by clicking "Control Panel" on the main interface, then clicking "Stop Server" and then "Start Server". Now you can use Formgrader to release and collect assignments.

If you're teaching several different courses, you will have to change ``mycourseid`` and use Formgrader to manage them one course at a time. You will have to restart your notebook server every time.

Students are not subject to this problem and can submit their assignments without a ``nbgrader_config.py`` file in their home directory.
