Course APIs
===========

/api/courses: Courses
---------------------

GET /api/courses
^^^^^^^^^^^^^^^^
List all available courses taking or teaching. (students+instructors)

List all courses in ngshare. (admins)

Used for ExchangeList.

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

Error messages
""""""""""""""
* 302 (Login required)

/api/course: Course
-------------------

POST /api/course/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Create a course (admins). Used for outside Exchange.*

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

Error messages
""""""""""""""
* 400 Instructors cannot be JSON decoded
* 409 Course already exists

DELETE /api/course/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Remove a course (admins). Used for outside Exchange.*

Response
""""""""
.. code:: javascript

    {
        "success": true
    }

Error messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found

/api/instructor: Course instructor management
---------------------------------------------

POST /api/instructor/<course_id>/<instructor_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Add or update a course instructor. (admins)*

*Update self full name or email. (instructors)*

If the user is already a student of the course, the student-relationship will be removed.

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

Error messages
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

When first name, last name, or email not set, the field is null

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

Error messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Instructor not found

DELETE /api/instructor/<course_id>/<instructor_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Remove a course instructor (admins)*

Submissions of the instructor are not removed.

Response
""""""""
.. code:: javascript

    {
        "success": true
    }

Error messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Instructor not found

/api/instructors: List course instructors
-----------------------------------------

GET /api/instructors/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Get information about all course instructors. (instructors+students)*

When first name, last name, or email not set, the field is null

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

Error messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found

/api/student: Student management
--------------------------------

POST /api/student/<course_id>/<student_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Add or update a student. (instructors only)*

Fails if the user is an instructor of the course

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

Error messages
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

When first name, last name, or email not set, the field is null

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

Error messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Student not found

DELETE /api/student/<course_id>/<student_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Remove a student (instructors only)*

Submissions of the student are not removed (visible to instructors).

Response
""""""""
.. code:: javascript

    {
        "success": true
    }

Error messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Student not found

/api/students: List course students
-----------------------------------

POST /api/students/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Add or update students. (instructors only)*

If the request syntax is correct, will return 200 and report whether each student is added correctly.

Request (HTTP POST data)
""""""""""""""""""""""""
.. code:: javascript

    students=[/* JSON object */
        {
            "username": "/* student 1 ID */",
            "first_name": "/* student 1 first name */",
            "last_name": "/* student 1 last name */",
            "email": "/* student 1 email */"
        },
        {
            "username": "/* student 2 ID */",
            "first_name": "/* student 2 first name */",
            "last_name": "/* student 2 last name */",
            "email": "/* student 2 email */"
        },
        ...
    ]

Response
""""""""
.. code:: javascript

    {
        "success": true
        "status": [
            {
                "username": "/* student 1 ID */",
                "success": true
            },
            {
                "username": "/* student 2 ID */",
                "success": false,
                "message": "Cannot add instructor as student"
            },
            ...
        ]
    }

Error messages
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

When first name, last name, or email not set, the field is null

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

Error messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found

