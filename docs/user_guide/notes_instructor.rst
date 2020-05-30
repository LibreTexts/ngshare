Notes for Instructors
=====================
Make sure to read the following to understand how to manage courses with ``ngshare``.

Course Creation
---------------
Only the administrators can create courses due to security concerns. Please contact your system administrator if you want to create a course. After they assign you as an instructor, you may manage the course roster and add more students to the course yourself.

Managing Students
-----------------
Please use the `ngshare-course-management <course_management.html>`_ tool when adding / removing students from a course. **Do not use Formgrader's interface to add students**, since this does not update ngshare.

Configuring nbgrader
-----------------------------------
By default, nbgrader needs a config file that specifies a single course under `c.CourseDirectory.course_id`. However, the special course ID ``*`` may be used to specify all available courses. This should be enabled by default by the administrator. If this isn't the case, you and all of your students must create a file called ``nbgrader_config.py`` in their home directories with the following contents:

.. code:: python

    c.CourseDirectory.course_id = 'mycourseid'

Replace ``mycourseid`` with the ID of the course. Afterwards, restart the notebook server by clicking "Control Panel" on the main interface, then clicking "Stop Server" and then "Start Server".

Using Formgrader
----------------
Formgrader does not support multiple classes, so you have to tell it which class you're currently teaching by explicitly specifying a course ID in ``nbgrader_config.py`` as mentioned above. The course ID may not be ``*``. If you see an error when releasing the assignment about ``ngshare endpoint /assignments/* returned failure: Course not found``, you haven't specified a course ID explicitly.

If you're teaching several different courses, you will have to change ``nbgrader_config.py`` and use Formgrader to manage them one course at a time. You will have to restart your notebook server every time.

Students are not subject to this problem and can submit their assignments without a ``nbgrader_config.py`` file in their home directory if ``c.CourseDirectory.course_id = '*'`` is specified globally in ``/etc/jupyter/nbgrader_config.py``.
