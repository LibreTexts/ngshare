
# Server API
Last updated 2020-03-08

---

## Definitions

### Assignment name
Also referred to as `assignment_id`, this is a unique name for an assignment within a course. For example, "Assignment 1".

### Checksum
The md5 checksum of a file.

### Course name
Also referred to as `course_id`, this is a unique name for a course. For example, "NBG 101".

### Notebook name
Also referred to as `notebook_id`, this is the base name of a .ipynb notebook without the extension. For example, "Problem 1" is the name for the notebook "Problem 1.ipynb".

### Instructor ID
The ID given to an instructor. For example, "course1_instructor" or "doe_jane"

### Student ID
The ID given to a student. For example, "doe_jane".

### Success
`true` if the request is successful, `false` otherwise. If unsuccessful, the response will only contain the fields `"success"` and `"message"`. The message field contains the error message, if any.

### Timestamp
A timestamp of when a user initiates the assignment submission process. It follows the [format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) `"%Y-%m-%d %H:%M:%S.%f %Z"`. For example, "2020-01-30 10:30:47.524219 UTC".

---

## Exchanging multiple files

### Directory tree
Assignments consist of a directory, notebook files in the root, and optional supplementary files in the root and/or subdirectories. In order to send an entire assignment in one request, a JSON file has a list of maps for each file. The following structure will be referred to as "encoded directory tree."

`path` should be in Unix style, and should be relative. For example: `a.ipynb` or `notes/a.txt`. Pathnames not following this style will be rejected by server with error "Illegal path".

```javascript
[
    {
        "path": /* file path relative to the root */,
        "content": /* base64 encoded file contents */,
        "checksum": /* md5 checksum of file contents */
    },
    ...
]
```

### Multiple directory trees and files
Each file and directory tree will be transferred individually.

---

## Authentication

(TODO)

---

## API specification
Adapted from [the proposed JupyterHub exchange service](https://github.com/jupyter/nbgrader/issues/659).

### /api/courses: Courses

#### GET /api/courses
*List all available courses taking or teaching (students+instructors).*

Used for ExchangeList.

##### Response
```javascript
{
    "success": true,
    "courses":
    [
        /* course name */,
        ...
    ]
}
```

##### Error messages
* Login required

### /api/course: Course

#### POST /api/course/&lt;course_id&gt;
*Create a course (anyone logged in). Used for outside Exchange.*

The new course will have no students. Its only instructor is the creator.

##### Response
```javascript
{
    "success": true
}
```

##### Error messages
* Login required
* Course already exists

### /api/instructor: Course instructor management

#### POST /api/instructor/&lt;course_id&gt;/&lt;instructor_id&gt;
*Add or update a course instructor. (instructors only)*

##### Request (HTTP POST data)
```
first_name=/*instructor first name*/&
last_name=/*instructor last name*/&
email=/*instructor email*/
```

##### Response
```javascript
{
    "success": true
}
```

##### Error messages
* Login required
* Permission denied
* Course not found

#### GET /api/instructor/&lt;course_id&gt;/&lt;instructor_id&gt;
*Get information about a course instructor. (instructors+students)*

##### Response
```javascript
{
    "success": true,
    "username": /* instructor ID */,
    "first_name": /* instructor name*/,
    "last_name": /* instructor last name*/,
    "email": /* instructor email*/
}
```

##### Error messages
* Login required
* Permission denied
* Course not found
* Instructor not found

#### DELETE /api/instructor/&lt;course_id&gt;/&lt;instructor_id&gt;
*Remove a course instructor (instructors only)*

##### Error messages
* Login required
* Permission denied
* Course not found
* Instructor not found
* Cannot remove last instructor

### /api/instructors: List course instructors

#### GET /api/instructors/&lt;course_id&gt;
*Get information about all course instructors. (instructors+students)*

##### Response
```javascript
{
    "success": true,
    "instructors":
    [
        {
            "username": /* instructor ID */,
            "first_name": /* instructor name*/,
            "last_name": /* instructor lastname */,
            "email": /* instructor email */
        },
        ...
    ]
}
```

#### Error messages
* Login required
* Permission denied
* Course not found

### /api/student: Student management

#### POST /api/student/&lt;course_id&gt;/&lt;student_id&gt;
*Create or update a student. (instructors only)*

##### Request (HTTP POST data)
```
first_name=/*student name*/&
last_name=/*student last name*/&
email=/*student email*/
```

##### Response
```javascript
{
    "success": true
}
```
##### Error messages
* Login required
* Permission denied
* Course not found

#### GET /api/student/&lt;course_id&gt;/&lt;student_id&gt;
*Get information about a student. (instructors+student with same student_id)*

##### Response
```javascript
{
    "success": true,
    "username": /* student ID */,
    "first_name": /* student first name*/,
    "last_name": /* student last name */,
    "email": /* student email */
}
```
##### Error messages
* Login required
* Permission denied
* Course not found
* Student not found

#### DELETE /api/student/&lt;course_id&gt;/&lt;student_id&gt;
*Remove a student (instructors only)*

##### Error messages
* Login required
* Permission denied
* Course not found
* Student not found

### /api/students: List course students

#### GET /api/students/&lt;course_id&gt;
*Get information about all course students. (instructors only)*

##### Response
```javascript
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
```
##### Error messages
* Login required
* Permission denied
* Course not found

### /api/assignments: Course assignments

#### GET /api/assignments/&lt;course_id&gt;
*list all assignments for a course (students+instructors)*

Used for the outbound part of ExchangeList.

##### Response
```javascript
{
    "success": true,
    "assignments":
    [
        /* assignment name */,
        ...
    ]
}
```

##### Error messages
* Login required
* Permission denied
* Course not found

### /api/assignment: Fetching and releasing an assignment

#### GET /api/assignment/&lt;course_id&gt;/&lt;assignment_id&gt;
*download a copy of an assignment (students+instructors)*

If `list_only` is `true`, `files` only contains `path` and `checksum` (does not contain `content`).

Used for ExchangeFetchAssignment.

##### Request (HTTP GET parameter)
```
list_only=/* true or false */
```

##### Response
```javascript
{
    "success": true,
    "files": /* encoded directory tree */
}
```

##### Error messages
* Login required
* Permission denied
* Course not found
* Assignment not found

#### POST /api/assignment/&lt;course_id&gt;/&lt;assignment_id&gt;
*release an assignment (instructors only)*

Used for ExchangeReleaseAssignment.

##### Request (HTTP POST data)
```
files=/* encoded directory tree in JSON */
```

##### Response
```javascript
{
    "success": true
}
```

##### Error messages
* Login required
* Permission denied
* Course not found
* Assignment already exists
* Please supply files
* Illegal path
* Files cannot be JSON decoded
* Content cannot be base64 decoded

### /api/submissions: Listing submissions

#### GET /api/submissions/&lt;course_id&gt;/&lt;assignment_id&gt;
*list all submissions for an assignment from all students (instructors only)*

Used for the inbound part of ExchangeList.

##### Response
```javascript
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
```

##### Error messages
* Login required
* Permission denied
* Course not found
* Assignment not found

#### GET /api/submissions/&lt;course_id&gt;/&lt;assignment_id&gt;/&lt;student_id&gt;
*list all submissions for an assignment from a particular student (instructors+students, though students are restricted to only viewing their own submissions)*

##### Response
```javascript
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
```

##### Error messages
* Login required
* Permission denied
* Course not found
* Assignment not found
* Student not found

### /api/submission: Collecting and submitting a submission

#### POST /api/submission/&lt;course_id&gt;/&lt;assignment_id&gt;
*submit a copy of an assignment (students+instructors)*

Used for ExchangeSubmit.

##### Request (HTTP POST data)
```
files=/* encoded directory tree in JSON */
```

##### Response
```javascript
{
    "success": true,
    "timestamp": /* submission timestamp */
}
```

##### Error messages
* Login required
* Permission denied
* Course not found
* Assignment not found
* Please supply files
* Illegal path
* Files cannot be JSON decoded
* Content cannot be base64 decoded

#### GET /api/submission/&lt;course_id&gt;/&lt;assignment_id&gt;/&lt;student_id&gt;
*download a student's submitted assignment (instructors only)*

If `list_only` is `true`, `files` only contains `path` and `checksum` (does not contain `content`). If `timestamp` is not supplied, the latest submision is returned.

Used for ExchangeCollect.

##### Request (HTTP GET parameter)
```
list_only=/* true or false */&
timestamp=/* submission timestamp */
```

##### Response
```javascript
{
    "success": true,
    "timestamp": /* submission timestamp */,
    "files": /* encoded directory tree */
}
```

##### Error messages
* Login required
* Permission denied
* Course not found
* Assignment not found
* Student not found
* Submission not found

### /api/feedback: Fetching and releasing submission feedback

#### POST /api/feedback/&lt;course_id&gt;/&lt;assignment_id&gt;/&lt;student_id&gt;
*upload feedback on a student's assignment (instructors only)*

Old feedback on the same submission will be removed

Used for ExchangeReleaseFeedback.

##### Request (HTTP POST data)
```
timestamp=/* submission timestamp */&
files=/* encoded directory tree in JSON */
```

##### Response
```javascript
{
    "success": true
}
```

##### Error messages
* Login required
* Permission denied
* Course not found
* Assignment not found
* Student not found
* Submission not found
* Please supply timestamp
* Time format incorrect
* Please supply files
* Illegal path
* Files cannot be JSON decoded
* Content cannot be base64 decoded

#### GET /api/feedback/&lt;course_id&gt;/&lt;assignment_id&gt;/&lt;student_id&gt;
*download feedback on a student's assignment (instructors+students, though students are restricted to only viewing their own feedback)*

When feedback is not available, `"files"` will be empty.

If `list_only` is `true`, `files` only contains `path` and `checksum` (does not contain `content`).

Used for ExchangeFetchFeedback.

##### Request (HTTP GET parameter)
```
timestamp=/* submission timestamp */&
list_only=/* true or false */
```
##### Response
```javascript
{
    "success": /* true or false*/,
    "timestamp": /* submission timestamp */,
    "files": /* encoded directory tree */
}
```
##### Error messages
* Login required
* Permission denied
* Course not found
* Assignment not found
* Student not found
* Submission not found
* Please supply timestamp
* Time format incorrect
