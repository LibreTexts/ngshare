# Server API

Last updated 2020-02-20

---

## Definitions

### Timestamp

A timestamp of when a user initiates the assignment submission process. It
follows the
[format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
"%Y-%m-%d %H:%M:%S.%f %Z". For example, "2020-01-30 10:30:47.524219 UTC".

---

## Exchanging multiple files

### Directory tree

Assignments consist of a directory, notebook files in the root, and optional supplementary files in the root and/or subdirectories. In order to send an entire assignment in one request, a JSON file has a list of maps for each file. The following structure will be referred to as "encoded directory tree."

```javascript
[
    {
        "path": /* file path relative to the root */,
        "content": /* base64 encoded file contents */
    },
    ...
]
```

### Multiple directory trees and files

Each file and directory tree will be transferred individually.

---

## API specification

Adapted from [the proposed JupyterHub exchange service](https://github.com/jupyter/nbgrader/issues/659).

### /api/courses: Courses

#### GET /api/courses

List all available courses (students+instructors). Used for ExchangeList.

##### Request

None

##### Response

```javascript
[
    /* course name */,
    ...
]
```

### /api/assignments: Course assignments

#### GET /api/assignments/&lt;course_id&gt;

*list all assignments for a course (students+instructors)*

Used for the outbound part of ExchangeList.

##### Request

None

##### Response

```javascript
{
    "success": /* true or false */,
    "assignments":
    [
        /* assignment name */,
        ...
    ]
}
```

### /api/assignment: Fetching and releasing an assignment

#### GET /api/assignment/&lt;course_id&gt;/&lt;assignment_id&gt;

*download a copy of an assignment (students+instructors)*

Used for ExchangeFetchAssignment.

##### Request

None

##### Response

```javascript
{
    "success": /* true or false */,
    "files": /* encoded directory tree */
}
```

#### POST /api/assignment/&lt;course_id&gt;/&lt;assignment_id&gt;

*release an assignment (instructors only)*

Used for ExchangeReleaseAssignment.

##### Request

```javascript
{
    "files": /* encoded directory tree */
}
```

##### Response

```javascript
{
    "success": /* true or false */
}
```

### /api/submissions: Listing submissions

#### GET /api/submissions/&lt;course_id&gt;/&lt;assignment_id&gt;

*list all submissions for an assignment from all students (instructors only)*

Used for the inbound part of ExchangeList.

##### Request

None

##### Response

```javascript
{
    "success": /* true or false */,
    "submissions":
    [
        {
            "student_id": /* student ID */,
            "timestamp": /* submission timestamp */,
            "notebooks":
            [
                {
                    "notebook_id": /* name of notebook */,
                    "feedback_checksum": /* md5 checksum, or "" */
                },
                ...
            ]
        },
        ...
    ]
}
```

#### GET /api/submissions/&lt;course_id&gt;/&lt;assignment_id&gt;/&lt;student_id&gt;

*list all submissions for an assignment from a particular student (instructors+students, though students are restricted to only viewing their own submissions)*

##### Request

None

##### Response

```javascript
{
    "success": /* true or false */,
    "submissions":
    [
        {
            "timestamp": /* submission timestamp */,
            "notebooks":
            [
                {
                    "notebook_id": /* name of notebook */,
                    "feedback_checksum": /* md5 checksum, or "" */
                },
                ...
            ]
        },
        ...
    ]
}
```

### /api/submission: Collecting and submitting a submission

#### POST /api/submission/&lt;course_id&gt;/&lt;assignment_id&gt;/&lt;student_id&gt;

*submit a copy of an assignment (students+instructors)*

Used for ExchangeSubmit.

##### Request

```javascript
{
    "timestamp": /* submission timestamp */,
    "files": /* encoded directory tree */
}
```

##### Response

```javascript
{
    "success": /* true or false */
}
```

#### GET /api/submission/&lt;course_id&gt;/&lt;assignment_id&gt;/&lt;student_id&gt;

*download a student's submitted assignment (instructors only)*

Used for ExchangeCollect.

##### Request

None

##### Response

```javascript
{
    "success": /* true or false */,
    "timestamp": /* submission timestamp */,
    "files": /* encoded directory tree */
}
```

### /api/feedback: Fetching and releasing submission feedback

#### POST /api/feedback/&lt;course_id&gt;/&lt;assignment_id&gt;/&lt;student_id&gt;

*upload feedback on a student's assignment (instructors only)*

Used for ExchangeReleaseFeedback.

##### Request

```javascript
[
    {
        "timestamp": /* submission timestamp */,
        "notebook_id": /* name of submitted notebook */,
        "file": /* base64 encoded content of feedback file */
    },
    ...
]
```

##### Response

```javascript
{
    "success": /* true or false */
}
```

#### GET /api/feedback/&lt;course_id&gt;/&lt;assignment_id&gt;/&lt;student_id&gt;

*download feedback on a student's assignment (instructors+students, though students are restricted to only viewing their own feedback)*

Used for ExchangeFetchFeedback.

##### Request

None

##### Response

```javascript
{
    "success": /* true or false*/,
    "feedback":
    [
        {
            "timestamp": /* submission timestamp */,
            "notebook_id": /* name of submitted notebook */,
            "file": /* base64 encoded content of feedback file */
        },
        ...
    ]
}
```
