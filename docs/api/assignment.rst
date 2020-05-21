Assignment APIs
===============

/api/assignments: Course Assignments
------------------------------------

GET /api/assignments/<course_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*list all assignments for a course (students+instructors)*

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "assignments":
        [
            /* assignment name */,
            ...
        ]
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found

/api/assignment: Fetching and Releasing an Assignment
-----------------------------------------------------

GET /api/assignment/<course_id>/<assignment_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*download a copy of an assignment (students+instructors)*

If ``list_only`` is ``true``, ``files`` only contains ``path`` and ``checksum`` (does not contain ``content``).

Request (HTTP GET parameter)
""""""""""""""""""""""""""""
.. code:: javascript

    list_only=/* true or false */

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "files": /* encoded directory tree */
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Assignment not found

POST /api/assignment/<course_id>/<assignment_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*release an assignment (instructors only)*

Request (HTTP POST data)
""""""""""""""""""""""""
.. code:: javascript

    files=/* encoded directory tree in JSON */

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
* 409 Assignment already exists
* 400 Please supply files
* 400 Illegal path
* 400 Files cannot be JSON decoded
* 400 Content cannot be base64 decoded
* 500 Internal server error

DELETE /api/assignment/<course_id>/<assignment_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Remove an assignment (instructors only).*

All submissions and files related to the assignment will disappear.

Note: this may be replaced by assignment states in the future.

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
* 404 Assignment not found

/api/submissions: Listing Submissions
-------------------------------------

GET /api/submissions/<course_id>/<assignment_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*list all submissions for an assignment from all students (instructors only)*

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "submissions":
        [
            {
                "student_id": /* student ID */,
                "timestamp": /* submission timestamp */
            },
            ...
        ]
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Assignment not found

GET /api/submissions/<course_id>/<assignment_id>/<student_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*list all submissions for an assignment from a particular student (instructors+students, though students are restricted to only viewing their own submissions)*

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "submissions":
        [
            {
                "student_id": /* student ID */,
                "timestamp": /* submission timestamp */
            },
            ...
        ]
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Assignment not found
* 404 Student not found

/api/submission: Collecting and Submitting a Submission
-------------------------------------------------------

POST /api/submission/<course_id>/<assignment_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*submit a copy of an assignment (students+instructors)*

Request (HTTP POST data)
""""""""""""""""""""""""
.. code:: javascript

    files=/* encoded directory tree in JSON */

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "timestamp": /* submission timestamp */
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Assignment not found
* 400 Please supply files
* 400 Illegal path
* 400 Files cannot be JSON decoded
* 400 Content cannot be base64 decoded
* 500 Internal server error

GET /api/submission/<course_id>/<assignment_id>/<student_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*download a student's submitted assignment (instructors only)*

If ``list_only`` is ``true``, ``files`` only contains ``path`` and ``checksum`` (does not contain ``content``). If ``timestamp`` is not supplied, the latest submision is returned.

Request (HTTP GET parameter)
""""""""""""""""""""""""""""
.. code:: javascript

    list_only=/* true or false */&
    timestamp=/* submission timestamp */

Response
""""""""
.. code:: javascript

    {
        "success": true,
        "timestamp": /* submission timestamp */,
        "files": /* encoded directory tree */
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Assignment not found
* 404 Student not found
* 404 Submission not found

/api/feedback: Fetching and Releasing Submission Feedback
---------------------------------------------------------

POST /api/feedback/<course_id>/<assignment_id>/<student_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*upload feedback on a student's assignment (instructors only)*

Old feedback on the same submission will be removed.

Request (HTTP POST data)
""""""""""""""""""""""""
.. code:: javascript

    timestamp=/* submission timestamp */&
    files=/* encoded directory tree in JSON */

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
* 404 Assignment not found
* 404 Student not found
* 404 Submission not found
* 400 Please supply timestamp
* 400 Time format incorrect
* 400 Please supply files
* 400 Illegal path
* 400 Files cannot be JSON decoded
* 400 Content cannot be base64 decoded
* 500 Internal server error

GET /api/feedback/<course_id>/<assignment_id>/<student_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*download feedback on a student's assignment (instructors+students, though students are restricted to only viewing their own feedback)*

When feedback is not available, ``files`` will be empty.

If ``list_only`` is ``true``, ``files`` only contains ``path`` and ``checksum`` (does not contain ``content``).

Request (HTTP GET parameter)
""""""""""""""""""""""""""""
.. code:: javascript

    timestamp=/* submission timestamp */&
    list_only=/* true or false */

Response
""""""""
.. code:: javascript

    {
        "success": /* true or false*/,
        "timestamp": /* submission timestamp */,
        "files": /* encoded directory tree */
    }

Error Messages
""""""""""""""
* 302 (Login required)
* 403 Permission denied
* 404 Course not found
* 404 Assignment not found
* 404 Student not found
* 404 Submission not found
* 400 Please supply timestamp
* 400 Time format incorrect
