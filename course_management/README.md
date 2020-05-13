# ngshare Course Management
## Flags
- `-c`, `--course_id` : A unique name for the course.
- `-s`, `--student_id` : The ID given to a student.
- `-i`, `--instructor_id` : The ID given to an instructor
- `-f`, `--first_name` : First name of the user you are creating
- `-l`, `--last_name` : Last name of the user you are creating
- `-e`, `--email` : Email of the user you are creating
- `--students_csv` : csv file containing a list of students to add. See `students.csv` as an example. 
- `--jhub` : Execute the command in ngshare and in JupyterHub
---
### Create a course
User creating course must be *admin*.
```
$ python3 ngshare_management.py create_course --course_id=math101
```
```
$ python3 ngshare_management.py create_course -c math101
```

### Add one student to a course:
```
$ python3 ngshare_management.py add_student --course_id=math101 --student_id=12345 --first_name=jane --last_name=doe --email=jdoe@mail.com 
```
```
$ python3 ngshare_management.py add_student -c math101 -s 12345 -f jane -l doe -e jdoe@mail.com
```

first name, last name, and email are optional parameters.

### Add multiple students to a course
```
$ python3 ngshare_management.py add_students --course_id=math101 --students_csv=math101Students.csv
```
```
$ python3 ngshare_management.py add_students -c math101 --students_csv=math101Students.csv
```

The csv file must have the following columns: **student_id**, **first_name**, **last_name**, **email**.

### Remove student from a course
```
$ python3 ngshare_management.py remove_student --course_id=math101 --student_id=12345
```
```
$ python3 ngshare_management.py remove_student -c math101 -s 12345
```

### Add instructor to a course
```
$ python3 ngshare_management.py add_instructor --course_id=math101 --instructor_id=12345 --first_name=jane --last_name=doe --email=jdoe@mail.com 
```
```
$ python3 ngshare_management.py add_instructor -c math101 -i 12345 -f jane -l doe -e jdoe@mail.com
```
first name, last name, and email are optional parameters

### Remove instructor from a course
```
$ python3 ngshare_management.py remove_instructor --course_id=math101 --instructor_id=12345
```
```
$ python3 ngshare_management.py remove_instructor -c math101 -i 12345
```
---
You can add the `--jhub` flag at the end of any command to execute the same action in JupyterHub.

For example running:
```
 $ python3 ngshare_management.py create_course --course_id=math101 --jhub
 ```
  creates the course in JupyterHub **and** ngshare
