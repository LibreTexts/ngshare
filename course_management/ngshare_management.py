import os
import sys
import getopt
import requests
import csv
import pwd
import grp
import subprocess
import json
import argparse

# https://www.geeksforgeeks.org/print-colors-python-terminal/
def prRed(skk):
    print("\033[91m {}\033[00m".format(skk))


def prGreen(skk):
    print("\033[92m {}\033[00m".format(skk))


class User:
    def __init__(self, id, first_name, last_name, email):
        self.id = id
        self.first_name = '' if first_name is None else first_name
        self.last_name = '' if last_name is None else last_name
        self.email = '' if email is None else email


def get_username():
    if 'JUPYTERHUB_USER' in os.environ:
        return os.environ['JUPYTERHUB_USER']
    else:
        return os.environ['USER']


def ngshare_url():
    if 'PROXY_PUBLIC_SERVICE_HOST' in os.environ:
        return "http://proxy-public/services/ngshare"
    else:
        # replace this with correct URL if you are not using a kubernetes set up
        return 'http://127.0.0.1:12121/api'


def get_header():
    if 'JUPYTERHUB_API_TOKEN' in os.environ:
        return {'Authorization': 'token ' + os.environ['JUPYTERHUB_API_TOKEN']}
    else:
        return None


def chown_to_user(path):
    uid = pwd.getpwnam(get_username()).pw_uid
    gid = grp.getgrnam(get_username()).gr_gid
    os.chown(path, uid, gid)


# https://stackoverflow.com/questions/1770209/run-child-processes-as-different-user-from-a-long-running-python-process/6037494#6037494
def demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)

    return result


# https://stackoverflow.com/questions/1770209/run-child-processes-as-different-user-from-a-long-running-python-process/6037494#6037494
def run_as_user(user_name, cwd, *args):
    pw_record = pwd.getpwnam(user_name)
    user_name = pw_record.pw_name
    user_home_dir = pw_record.pw_dir
    user_uid = pw_record.pw_uid
    user_gid = pw_record.pw_gid
    cwd = user_home_dir if cwd == '~' else cwd
    env = os.environ.copy()
    env['HOME'] = user_home_dir
    env['LOGNAME'] = user_name
    env['PWD'] = cwd
    env['USER'] = user_name
    process = subprocess.Popen(
        args, preexec_fn=demote(user_uid, user_gid), cwd=cwd, env=env
    )
    return process.wait()


def check_status_code(response):
    if response.status_code != requests.codes.ok:
        prRed(
            'ngshare returned an invalid status code {}'.format(
                response.status_code
            )
        )
        check_message(response)


def check_message(response):
    response = response.json()
    if not response['success']:
        prRed(response['message'])
        return None

    return response


def post(url, data):
    header = get_header()

    try:
        response = requests.post(url, data=data, headers=header)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        prRed('Could not establish connection to ngshare server')
        return None
    except Exception:
        check_status_code(response)
        return None

    return check_message(response)


def delete(url, data):
    header = get_header()

    try:
        response = requests.delete(url, data=data, headers=header)
        response.raise_for_status
    except Exception:
        check_status_code(response)
        return None

    return check_message(response)


def create_course(course_id, jhub):
    prGreen('Creating ngshare course {}'.format(course_id))
    url = '{}/course/{}'.format(ngshare_url(), course_id)
    data = {'user': get_username()}

    response = post(url, data)

    if response is None:
        prRed(
            'An error occurred while trying to create the course {}'.format(
                course_id
            )
        )
        return None
    else:
        prGreen(
            'Successfully created {} with {} as the instructor.'.format(
                course_id, get_username()
            )
        )

    if jhub:
        create_jh_course(course_id)


def create_jh_course(course_id):
    prGreen('Creating JupyterHub course {}'.format(course_id))

    # create course root directory
    course_root_dir = '/home/{}/{}'.format(get_username(), course_id)
    if not os.path.exists(course_root_dir):
        os.mkdir(course_root_dir)
    else:
        prRed('{} already exists'.format(course_root_dir))
        return None

    # change owner
    chown_to_user(course_root_dir)

    # add course config file
    course_config_file = course_root_dir + '/nbgrader_config.py'
    with open(course_config_file, 'w') as f:
        f.write('c = get_config()\n')
        f.write("c.CourseDirectory.course_id = '{}'".format(course_id))

    # create .jupyter folder
    jupyter_folder = '/home/{}/.jupyter'.format(get_username())
    if not os.path.exists(jupyter_folder):
        os.mkdir(jupyter_folder)

    # add user config file in the .jupyter folder
    user_config_file = '{}/nbgrader_config.py'.format(jupyter_folder)
    with open(user_config_file, 'w') as f:
        f.write('c = get_config()\n')
        f.write("c.CourseDirectory.root = '{}'".format(course_root_dir))

    prGreen('Successfully created JupyterHub course {}.'.format(course_id))


def add_student(course_id, student: User, jhub):
    # add student to ngshare
    url = '{}/student/{}/{}'.format(ngshare_url(), course_id, student.id)
    data = {
        'user': get_username(),
        'first_name': student.first_name,
        'last_name': student.last_name,
        'email': student.email,
    }

    response = post(url, data)

    if response is None:
        prRed(
            'An error occurred while trying to add {} to {}'.format(
                student.id, course_id
            )
        )
        return None
    else:
        prGreen('Successfully added {} to {}'.format(student.id, course_id))

    if jhub:
        add_jh_student(course_id, student)


def add_jh_student(course_id, student: User):
    # add student to nbgrader database
    ret = run_as_user(
        get_username(),
        os.getcwd(),
        'nbgrader',
        'db',
        'student',
        'add',
        '--first-name',
        student.first_name,
        '--last-name',
        student.last_name,
        '--email',
        student.email,
        student.id,
    )

    if ret == 0:
        prGreen('Successfully added {} to nbgrader database'.format(student.id))


def add_students(course_id, students_csv, jhub):
    students = []
    with open(students_csv, 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        header = next(csv_reader)

        required_cols = ['student_id', 'first_name', 'last_name', 'email']

        cols_dict = dict()
        for i, col in enumerate(header):
            cols_dict[col] = i

        for col in required_cols:
            if col not in cols_dict:
                prRed('Missing column {} in {}.'.format(col, students_csv))
                sys.exit(1)

        for i, row in enumerate(csv_reader):
            student_dict = {}
            student_id = row[cols_dict['student_id']]
            if len(student_id.replace(' ', '')) == 0:
                prRed('Student ID cannot be empty (row {})'.format(i + 1))
                continue
            first_name = row[cols_dict['first_name']]
            last_name = row[cols_dict['last_name']]
            email = row[cols_dict['email']]

            student_dict['username'] = student_id
            student_dict['first_name'] = first_name
            student_dict['last_name'] = last_name
            student_dict['email'] = email
            students.append(student_dict)
            student = User(student_id, first_name, last_name, email)
            if jhub:
                add_jh_student(course_id, student)

    url = '{}/students/{}'.format(ngshare_url(), course_id)
    data = {'user': get_username(), 'students': json.dumps(students)}

    response = post(url, data)

    if response is None:
        prRed(
            'An error occurred while trying to add students to the course {}'.format(
                course_id
            )
        )
        return None
    else:

        if response['success']:
            for s in response['status']:
                user = s['username']
                if s['success']:
                    prGreen(
                        '{} was sucessfuly added to {}'.format(user, course_id)
                    )
                else:
                    prRed(
                        'There was an error adding {} to {}: {}'.format(
                            user, course_id, s['message']
                        )
                    )


def remove_student(course_id, student_id):
    url = '{}/student/{}/{}'.format(ngshare_url(), course_id, student_id)
    data = {'user': get_username()}
    response = delete(url, data)

    if response is None:
        prRed(
            'An error occurred while trying to delete {} from {}'.format(
                student_id, course_id
            )
        )
    else:
        prGreen('Successfully deleted {} from {}'.format(student_id, course_id))


def add_instructor(course_id, instructor: User):
    url = '{}/instructor/{}/{}'.format(ngshare_url(), course_id, instructor.id)
    data = {
        'user': get_username(),
        'first_name': instructor.first_name,
        'last_name': instructor.last_name,
        'email': instructor.email,
    }
    response = post(url, data)

    if response is None:
        prRed(
            'An error occurred while trying to add {} as an instructor to {}'.format(
                instructor.id, course_id
            )
        )
    else:
        prGreen(
            'Successfully added {} as an instructor to {}'.format(
                instructor.id, course_id
            )
        )


def remove_instructor(course_id, instructor_id):
    url = '{}/instructor/{}/{}'.format(ngshare_url(), course_id, instructor_id)
    data = {'user': get_username()}
    response = delete(url, data)

    if response is None:
        prRed(
            'An error occurred while trying to delete {} from {}'.format(
                instructor_id, course_id
            )
        )
    else:
        prGreen(
            'Successfully deleted instructor {} from {}'.format(
                instructor_id, course_id
            )
        )


def parse_input(argv):
    parser = argparse.ArgumentParser(description='ngshare Course Management')
    parser.add_argument(
        '-c', '--course_id', default=None, help="A unique name for the course"
    )
    parser.add_argument(
        '-s', '--student_id', default=None, help="The ID given to a student"
    )
    parser.add_argument(
        '-i',
        '--instructor_id',
        default=None,
        help="The ID given to an instructor",
    )
    parser.add_argument(
        '-f',
        '--first_name',
        default=None,
        help="First name of the user you are creating",
    )
    parser.add_argument(
        '-l',
        '--last_name',
        default=None,
        help="Last name of the user you are creating",
    )
    parser.add_argument(
        '-e',
        '--email',
        default=None,
        help="Last name of the user you are creating",
    )
    parser.add_argument(
        '--students_csv',
        default=None,
        help="csv file containing a list of students to add. See students.csv as an example.",
    )
    parser.add_argument(
        'command',
        action='store',
        type=str,
        choices=[
            'create_course',
            'add_student',
            'add_students',
            'remove_student',
            'add_instructor',
        ],
        help='Command to execute',
    )
    parser.add_argument(
        '--jhub',
        default=False,
        help="Execute the command in ngshare and in JupyterHub",
    )

    args = parser.parse_args()

    return args


def execute_command(args):
    command = args.command
    course_id = args.course_id
    student_id = args.student_id
    instructor_id = args.instructor_id
    first_name = args.first_name
    last_name = args.last_name
    email = args.email
    students_csv = args.students_csv
    jhub = args.jhub

    if command == 'create_course' and course_id:
        create_course(course_id, jhub)
    elif command == 'add_student' and course_id and student_id:
        student = User(student_id, first_name, last_name, email)
        add_student(course_id, student, jhub)
    elif command == 'add_students' and course_id and students_csv:
        add_students(course_id, students_csv, jhub)
    elif command == 'remove_student' and course_id and student_id:
        remove_student(course_id, student_id)
    elif command == 'add_instructor' and course_id and instructor_id:
        instructor = User(instructor_id, first_name, last_name, email)
        add_instructor(course_id, instructor)
    elif command == 'remove_instructor' and course_id and instructor_id:
        remove_instructor(course_id, instructor_id)
    else:
        prRed(
            'The command you entered was not recognized. Use the --help flag to see usage examples'
        )


def main(argv=None):

    argv = argv or sys.argv
    args = parse_input(argv)
    execute_command(args)


if __name__ == '__main__':

    sys.exit(main())
