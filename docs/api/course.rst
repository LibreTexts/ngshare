Course APIs
===========

/api/courses: Courses
---------------------

GET /api/courses
^^^^^^^^^^^^^^^^
*List all available courses taking or teaching. (students+instructors)*

*List all courses in ngshare. (admins)*

Response
""""""""

.. code:: javascript

    {
        "success": true,
        "courses":
        [
            /* course name */,
            ...
        ]
    }

Error Messages
""""""""""""""
* 302 (Login required)

/api/course: Course
-------------------

POST /api/course/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Create a course (admins).*

The new course will have no students. It has no instructors unless specified in request. 

Request (HTTP POST data)
""""""""""""""""""""""""
.. code:: javascript

    instructors=["/*instructor username*/", ...] /* optional */

Response
""""""""
.. code:: javascript

    {
        "success": true
    }

Error Messages
""""""""""""""
* 400 Instructors cannot be JSON decoded
* 409 Course already exists

DELETE /api/course/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Remove a course (admins).*

Response
""""""""
.. code:: javascript

    {
        "success": true
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found

/api/instructor: Course Instructor Management
---------------------------------------------

POST /api/instructor/<course_id>/<instructor_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Add or update a course instructor. (admins)*

*Update own full name or email. (instructors)*

If the user is already a student of the course, the student relationship will be removed.

Request (HTTP POST data)
""""""""""""""""""""""""
.. code:: javascript

    first_name=/*instructor first name*/&
    last_name=/*instructor last name*/&
    email=/*instructor email*/

Response
""""""""
.. code:: javascript

    {
        "success": true
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 400 Please supply first name
* 400 Please supply last name
* 400 Please supply email name

GET /api/instructor/<course_id>/<instructor_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Get information about a course instructor. (instructors+students)*

When first name, last name, or email not set, the field is null.

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "username": /* instructor ID */,
        "first_name": /* instructor first name*/,
        "last_name": /* instructor last name*/,
        "email": /* instructor email*/
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Instructor not found

DELETE /api/instructor/<course_id>/<instructor_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Remove a course instructor (admins)*

The instructor's submissions are not removed from the course.

Response
""""""""
.. code:: javascript

    {
        "success": true
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Instructor not found

/api/instructors: List Course Instructors
-----------------------------------------

GET /api/instructors/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Get information about all course instructors. (instructors+students)*

When first name, last name, or email not set, the field is null.

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "instructors":
        [
            {
                "username": /* instructor ID */,
                "first_name": /* instructor first name*/,
                "last_name": /* instructor last name */,
                "email": /* instructor email */
            },
            ...
        ]
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found

/api/student: Student Management
--------------------------------

POST /api/student/<course_id>/<student_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Add or update a student. (instructors only)*

Fails if the user is an instructor of the course.

Request (HTTP POST data)
""""""""""""""""""""""""
.. code:: javascript

    first_name=/*student first name*/&
    last_name=/*student last name*/&
    email=/*student email*/

Response
""""""""
.. code:: javascript

    {
        "success": true
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 409 Cannot add instructor as student
* 400 Please supply first name
* 400 Please supply last name
* 400 Please supply email

GET /api/student/<course_id>/<student_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Get information about a student. (instructors+student with same student_id)*

When first name, last name, or email not set, the field is null.

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "username": /* student ID */,
        "first_name": /* student first name*/,
        "last_name": /* student last name */,
        "email": /* student email */
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Student not found

DELETE /api/student/<course_id>/<student_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Remove a student (instructors only)*

The student's submissions are not removed from the course (visible to instructors).

Response
""""""""
.. code:: javascript

    {
        "success": true
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Student not found

/api/students: List Course Students
-----------------------------------

POST /api/students/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Add or update students. (instructors only)*

If the request syntax is correct, will return 200 and report whether each student is added correctly.

Request (HTTP POST data)
""""""""""""""""""""""""
.. code:: javascript

    {
        "students":
        [
            {
                "username": /* student ID */,
                "first_name": /* student first name */,
                "last_name": /* student last name */,
                "email": /* student email */
            },
            ...
        ]
    }

Response
""""""""
.. code:: javascript

    {
        "success": true
        "status":
        [
            {
                "username": /* student ID */,
                "success": true
            },
            {
                "username": /* student ID */,
                "success": false,
                "message": /* error message */
            },
            ...
        ]
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 400 Please supply students
* 400 Students cannot be JSON decoded
* 400 Incorrect request format

GET /api/students/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Get information about all course students. (instructors only)*

When first name, last name, or email not set, the field is null.

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "students":
        [
            {
                "username": /* student ID */,
                "first_name": /* student first name*/,
                "last_name": /* student last name */,
                "email": /* student email */
            },
            ...
        ]
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
