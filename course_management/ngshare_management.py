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
def prRed(skk, exit=True):
    print('\033[91m {}\033[00m'.format(skk))

    if exit:
        sys.exit(-1)


def prGreen(skk):
    print('\033[92m {}\033[00m'.format(skk))


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
        return 'http://proxy-public/services/ngshare'
    else:
        # replace this with correct URL if you are not using a kubernetes set up
        return 'http://127.0.0.1:12121/api'


def get_header():
    if 'JUPYTERHUB_API_TOKEN' in os.environ:
        return {'Authorization': 'token ' + os.environ['JUPYTERHUB_API_TOKEN']}
    else:
        return None


def check_status_code(response):
    if response.status_code != requests.codes.ok:
        prRed(
            'ngshare returned an invalid status code {}'.format(
                response.status_code
            ),
            False,
        )
        if response.status_code >= 500:
            prRed(
                'ngshare encountered an error. Please contact the maintainers'
            )

        check_message(response)


def check_message(response):

    response = response.json()
    if not response['success']:
        prRed(response['message'])

    return response


def post(url, data):
    header = get_header()

    try:
        response = requests.post(url, data=data, headers=header)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        prRed('Could not establish connection to ngshare server')
    except Exception:
        check_status_code(response)

    return check_message(response)


def delete(url, data):
    header = get_header()

    try:
        response = requests.delete(url, data=data, headers=header)
        response.raise_for_status
    except Exception:
        check_status_code(response)

    return check_message(response)


def create_course(course_id, instructors):
    url = '{}/course/{}'.format(ngshare_url(), course_id)
    data = {'user': get_username(), 'instructors': json.dumps(instructors)}

    response = post(url, data)
    prGreen('Successfully created {}'.format(course_id))


def add_student(course_id, student: User, gb):
    # add student to ngshare
    url = '{}/student/{}/{}'.format(ngshare_url(), course_id, student.id)
    data = {
        'user': get_username(),
        'first_name': student.first_name,
        'last_name': student.last_name,
        'email': student.email,
    }

    response = post(url, data)
    prGreen('Successfully added/updated {} on {}'.format(student.id, course_id))

    if gb:
        add_jh_student(student)


def add_jh_student(student: User):
    # add student to nbgrader gradebook
    command = 'nbgrader db student add '

    if len(student.first_name) > 0:
        command += '--first-name {} '.format(student.first_name)
    if len(student.last_name) > 0:
        command += '--last-name {} '.format(student.last_name)
    if len(student.email) > 0:
        command += '--email {} '.format(student.email)

    command += student.id
    os.system(command)


def add_students(course_id, students_csv, gb):
    students = []
    with open(students_csv, 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        rows = list(csv_reader)
        if len(rows) == 0:
            prRed('The csv file you entered is empty')

        header = rows[0]

        required_cols = ['student_id', 'first_name', 'last_name', 'email']

        cols_dict = dict()
        for i, col in enumerate(header):
            cols_dict[col] = i

        for col in required_cols:
            if col not in cols_dict:
                prRed('Missing column {} in {}.'.format(col, students_csv))

        for i, row in enumerate(rows[1:]):
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

    url = '{}/students/{}'.format(ngshare_url(), course_id)
    data = {'user': get_username(), 'students': json.dumps(students)}

    response = post(url, data)

    if response['success']:
        for i, s in enumerate(response['status']):
            user = s['username']
            if s['success']:
                prGreen('{} was sucessfuly added to {}'.format(user, course_id))
                student = User(
                    user,
                    students[i]['first_name'],
                    students[i]['last_name'],
                    students[i]['email'],
                )
                if gb:
                    add_jh_student(student)
            else:
                prRed(
                    'There was an error adding {} to {}: {}'.format(
                        user, course_id, s['message']
                    ),
                    False,
                )


def remove_jh_student(student_id, force):
    # remove a student from nbgrader gradebook
    command = 'nbgrader db student remove {} '.format(student_id)
    if force:
        command += '--force'
    os.system(command)


def remove_student(course_id, student_id, gb, force):
    if gb:
        remove_jh_student(student_id, force)

    url = '{}/student/{}/{}'.format(ngshare_url(), course_id, student_id)
    data = {'user': get_username()}
    response = delete(url, data)
    prGreen('Successfully deleted {} from {}'.format(student_id, course_id))


def add_instructor(course_id, instructor: User):
    url = '{}/instructor/{}/{}'.format(ngshare_url(), course_id, instructor.id)
    data = {
        'user': get_username(),
        'first_name': instructor.first_name,
        'last_name': instructor.last_name,
        'email': instructor.email,
    }
    print(data)
    response = post(url, data)
    prGreen(
        'Successfully added {} as an instructor to {}'.format(
            instructor.id, course_id
        )
    )


def remove_instructor(course_id, instructor_id):
    url = '{}/instructor/{}/{}'.format(ngshare_url(), course_id, instructor_id)
    data = {'user': get_username()}
    response = delete(url, data)
    prGreen(
        'Successfully deleted instructor {} from {}'.format(
            instructor_id, course_id
        )
    )


def parse_input(argv):
    parser = argparse.ArgumentParser(description='ngshare Course Management')
    parser.add_argument(
        '-c', '--course_id', default=None, help='A unique name for the course'
    )
    parser.add_argument(
        '-s', '--student_id', default=None, help='The ID given to a student'
    )
    parser.add_argument(
        '-i',
        '--instructor_id',
        default=None,
        help='The ID given to an instructor',
    )
    parser.add_argument(
        '-f',
        '--first_name',
        default=None,
        help='First name of the user you are creating',
    )
    parser.add_argument(
        '-l',
        '--last_name',
        default=None,
        help='Last name of the user you are creating',
    )
    parser.add_argument(
        '-e',
        '--email',
        default=None,
        help='Last name of the user you are creating',
    )
    parser.add_argument(
        '--students_csv',
        default=None,
        help='csv file containing a list of students to add. See students.csv as an example.',
    )

    parser.add_argument(
        '--instructors',
        nargs='*',
        default=[],
        help='List of course instructors',
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
            'remove_instructor',
        ],
        help='Command to execute',
    )
    parser.add_argument(
        '--gb',
        action='store_true',
        default=False,
        help='Add student to nbgrader gradebook',
    )

    parser.add_argument(
        '--force',
        action='store_true',
        default=False,
        help='Force gradebook action',
    )

    args = parser.parse_args()

    return args


def execute_command(args):
    command = args.command
    course_id = args.course_id
    student_id = args.student_id
    instructor_id = args.instructor_id
    instructors = args.instructors
    first_name = args.first_name
    last_name = args.last_name
    email = args.email
    students_csv = args.students_csv
    gb = args.gb
    force = args.force

    if command == 'create_course':
        if not course_id:
            prRed(
                'Please specify the course_id for the course with -c or --course_id'
            )
        create_course(course_id, instructors)
    elif command == 'add_student':
        if not course_id:
            prRed(
                'Please specify the course you want to add the student to using -c or --course_id'
            )
        if not student_id:
            prRed(
                'Please specify the student you want to add using -s or --student_id'
            )
        student = User(student_id, first_name, last_name, email)
        add_student(course_id, student, gb)
    elif command == 'add_students':
        if not course_id:
            prRed(
                'Please specify the course you want to add the students to using -c or --course_id'
            )
        if not students_csv:
            prRed(
                'Please enter the path containing the students csv using --students_csv'
            )
        if not os.path.exists(students_csv):
            prRed(
                'The csv file you entered does not exist. Please enter a valid path using --students_csv'
            )
        add_students(course_id, students_csv, gb)
    elif command == 'remove_student':
        if not course_id:
            prRed(
                'Please specify which course you want to remove the student from using -c or --course_id'
            )
        if not student_id:
            prRed(
                'Please specify the student you want to remove from the course using -s or --student_id'
            )
        remove_student(course_id, student_id, gb, force)
    elif command == 'add_instructor':
        if not course_id:
            prRed(
                'Please specify the course you want to add the instructor to using -c or --course_id'
            )
        if not instructor_id:
            prRed(
                'Please specify the instructor you want to add using -i or --instructor_student'
            )
        instructor = User(instructor_id, first_name, last_name, email)
        add_instructor(course_id, instructor)
    elif command == 'remove_instructor':
        if not course_id:
            prRed(
                'Please specify which course you want to remove the instructor from using -c or --course_id'
            )
        if not instructor_id:
            prRed(
                'Please specify the instructor you want to remove using -i or --instructor_id'
            )
        remove_instructor(course_id, instructor_id)

    return True


def main(argv=None):

    argv = argv or sys.argv
    parsed_args = parse_input(argv)
    execute_command(parsed_args)


if __name__ == '__main__':

    sys.exit(main())
