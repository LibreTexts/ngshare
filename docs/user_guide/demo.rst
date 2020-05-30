Demo
====
For this demo, you need to setup a clean environment using JupyterHub + nbgrader + ngshare. 
.. You can use the [minikube testing setup](/testing#testing-setup) to do it easily.

Creating Course
---------------
1. Login as user "admin". 
2. Open a terminal using "New -> Terminal"
3. Create a course with two instructors using

.. code::

    ngshare-course-management create_course ECS193 kevin abigail

.. All usernames are login-able with any passwords.

Adding Students
---------------
1. Login as user "kevin".
2. Open a terminal using "New -> Terminal"
3. Add students to the course using

.. code::

    ngshare-course-management add_student ECS193 lawrence -f lawrence_first -l lawrence_last -e lawrence@email
    ngshare-course-management add_student ECS193 eric -f eric_first -l eric_last -e eric@email

4. Create a new file with "New -> Text File", name it ``nbgrader_config.py`` and add the following content:

.. code::

    c.CourseDirectory.course_id = "ECS193"

5. Go to "Control Panel", click on "Stop My Server"
6. Click on "Start My Server"
7. Go to "Formgrader -> Manage Students". You should see the two students created before.

Releasing Assignment
--------------------
0. Make sure you are logged in as user "kevin".
1. Go to "Formgrader -> Manage Assignments".
2. Click "Add new assignment...".
3. Click on the name of the assignment you just added.
4. "New -> Notebook -> Python 3", and edit the notebook as in normal nbgrader.

	1. Add some code to the block.
	2. "View -> Cell Toolbar -> Create Assignment".
	3. Select "Autograded answer".
	4. ...
	5. Save notebook.

5. Click the button under "Generate" in Formgrader.
6. Click the button under "Release".

Doing Assignment
----------------
1. Login as user "lawrence" (you may want to use incognito mode).
2. Go to "Assignments" tab.
3. Click "Fetch" for the new assignment.
4. Click on the assignment name and the ipyndb name to open the homework.
5. Do your homework.
6. Click "Submit" in "Assignments -> Downloaded assignments".

Grading Assignment
------------------
0. Make sure you are logged in as user "kevin".
1. Go to "Formgrader -> Manage Assignments".
2. Click the button under "Collect" in Formgrader. 
3. You should see "1" under "# Submissions". Click on this number. 
4. Click the button under "Autograde" in Manage Submissions. 
5. Click Student Name, and then the notebook name to open the submission.
6. Write some feedback for the student.
7. Click "Next" at upper right corner.
8. Go back to "Manage Assignments".
9. Click the button under "Generate Feedback".
10. Click the button under "Release Feedback".

Viewing Feedback
----------------
0. Make sure you are logged in as user "lawrence".
1. Under "Assignments", click "Fetch Feedback"
2. Click "(view feedback)". 
3. Click notebook name.
4. Now you can see the html feedback. 

