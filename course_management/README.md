# ngshare Course Management
## Flags
- `-c`, `--course_id` : A unique name for the course.
- `-s`, `--student_id` : The ID given to a student.
- `-i`, `--instructor_id` : The ID given to an instructor
- `-f`, `--first_name` : First name of the user you are creating
- `-l`, `--last_name` : Last name of the user you are creating
- `-e`, `--email` : Email of the user you are creating
- `--students_csv` : csv file containing a list of students to add. See `students.csv` as an example. 
- `--gb` : add/update the student to the nbgrader gradebook
---
### Create a course
User creating course must be *admin*.
admin must specify the instructor of the course.

```
$ python3 ngshare_management.py create_course --course_id=math101 --instructor_id=123
```
```
$ python3 ngshare_management.py create_course -c math101 -i
```

Remember to add the `nbgrader_config.py` on the course root directory e.g. `/home/username/math101`
Example course configuration file:
```python
c = get_config()
c.CourseDirectory.course_id = 'math101'
```

Also, remember to add the `nbgrader_config.py` on the instructor's `/home/username/.jupyter` folder.
Example user configuration file:
```python
c = get_config()
c.CourseDirectory.root = '/home/username/math101'
```

### Add/update one student
```
$ python3 ngshare_management.py add_student --course_id=math101 --student_id=12345 --first_name=jane --last_name=doe --email=jdoe@mail.com 
```
```
$ python3 ngshare_management.py add_student -c math101 -s 12345 -f jane -l doe -e jdoe@mail.com
```

first name, last name, and email are optional parameters.

### Add/update multiple students
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
You can add the `--gb` flag at the end of `add_student`, `add_students`, or `remove_student` to add or remove the students from the nbgrader gradebook **and** ngshare

For example running:
```
 $ python3 ngshare_management.py add_student -c math101 -s 12345 -f jane -l doe -e jdoe@mail.com --gb
 ```

Adding the --gb flag runs:
```
 $ nbgrader db student add --first-name jane --last-name doe --email jdoe@mail.com 12345
```
