import base64
import os

import pytest
import re
from logging import getLogger
import requests
from requests import PreparedRequest
import requests_mock as rq_mock
from requests_mock import Mocker
import urllib
import tempfile
import ngshare_management as nm
from io import StringIO


class Command:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def remove_color(s):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    result = ansi_escape.sub('', s)
    return result


def parse_body(body: str):
    # https://stackoverflow.com/questions/48018622/how-can-see-the-request-data#51052385
    return dict(urllib.parse.parse_qsl(body))


NGSHARE_URL = 'http://127.0.0.1:12121/api'


class TestCourseManagement:
    course_id = 'math101'
    instructor = (
        os.environ['JUPYTERHUB_USER']
        if 'JUPYTERHUB_USER' in os.environ
        else os.environ['USER']
    )
    instructors = ['mi1', 'mi2']
    student_id = 'ms'
    instructor_id = 'mi1'

    course_created = False

    @pytest.fixture(autouse=True)
    def init(self, requests_mock: Mocker):
        self.requests_mocker = requests_mock
        requests_mock.register_uri(
            rq_mock.ANY, rq_mock.ANY, text=self._mock_all
        )

    def form_command(
        self,
        command,
        course_id=None,
        student_id=None,
        instructor_id=None,
        instructors=[],
        first_name=None,
        last_name=None,
        email=None,
        students_csv=None,
        gb=False,
        force=False,
    ):
        return Command(
            command=command,
            course_id=course_id,
            student_id=student_id,
            instructor_id=instructor_id,
            instructors=instructors,
            first_name=first_name,
            last_name=last_name,
            email=email,
            students_csv=students_csv,
            gb=gb,
            force=force,
        )

    def _mock_all(self, request: PreparedRequest, content):
        getLogger().fatal(
            'The request \'%s\' has not been mocked yet.', request.url
        )
        content.status_code = 404
        return ''

    def _get_user_info(self, request: PreparedRequest, context):
        request = parse_body(request.body)
        if 'first_name' not in request:
            return {'success': False, 'message': 'Please supply first name'}
        elif 'last_name' not in request:
            return {'success': False, 'message': 'Please supply last name'}
        elif 'email' not in request:
            return {'success': False, 'message': 'Please supply email'}
        elif request['user'] != self.instructor:
            return {'success': False, 'message': 'Permission denied'}
        else:
            return {'success': True}

    def _get_students_info(self, request: PreparedRequest, context):
        request = parse_body(request.body)
        students = eval(request['students'])

        if (
            'sid1' == students[0]['username']
            and 'sid2' == students[1]['username']
        ):
            return {
                'success': True,
                'status': [
                    {'username': 'sid1', 'success': True},
                    {'username': 'sid2', 'success': True},
                ],
            }
        else:
            return {'success': False, 'message': 'wrong students passed in'}

    def _get_user(self, request: PreparedRequest, context):
        request = parse_body(request.body)
        response = {'success': False, 'message': 'Permission denied'}
        if self.instructor in request['user']:
            response = {'success': True}
        return response

    def _get_instructors_info(self, request: PreparedRequest, context):
        request = parse_body(request.body)
        response = {'success': False, 'message': 'Some error occurred'}
        if not self.course_created:
            if 'instructors' in request:
                instructors = eval(request['instructors'])
                if (
                    self.instructors[0] == instructors[0]
                    and self.instructors[1] == instructors[1]
                ):
                    response = {'success': True}
                    self.course_created = True
        else:
            response = {'success': False, 'message': 'Course already exists'}

        return response

    def _mock_create_course(self):
        url = '{}/course/{}'.format(NGSHARE_URL, self.course_id)
        self.requests_mocker.post(url, json=self._get_instructors_info)

    def _mock_add_student(self):
        url = '{}/student/{}/{}'.format(
            NGSHARE_URL, self.course_id, self.student_id
        )
        self.requests_mocker.post(url, json=self._get_user_info)

    def _mock_add_students(self):
        url = '{}/students/{}'.format(
            NGSHARE_URL, self.course_id, self.student_id
        )
        self.requests_mocker.post(url, json=self._get_students_info)

    def _mock_add_instructor(self):
        url = '{}/instructor/{}/{}'.format(
            NGSHARE_URL, self.course_id, self.instructor_id
        )
        self.requests_mocker.post(url, json=self._get_user_info)

    def _mock_remove_student(self):
        url = '{}/student/{}/{}'.format(
            NGSHARE_URL, self.course_id, self.student_id
        )
        self.requests_mocker.delete(url, json=self._get_user)

    def _mock_remove_instructor(self):
        url = '{}/instructor/{}/{}'.format(
            NGSHARE_URL, self.course_id, self.instructor_id
        )
        self.requests_mocker.delete(url, json=self._get_user)

    def test_crete_course(self, capsys):
        self._mock_create_course()
        cmd = self.form_command(
            'create_course',
            course_id=self.course_id,
            instructors=self.instructors,
        )
        nm.execute_command(cmd)
        out, err = capsys.readouterr()
        out = remove_color(out)
        assert ' Successfully created {}\n'.format(self.course_id) in out

        # test missing course id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('create_course')
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # try to create course again
        self._mock_create_course()
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('create_course', course_id=self.course_id)
            nm.execute_command(cmd)
        out, err = capsys.readouterr()
        assert ' Course already exists' in out
        assert se.type == SystemExit
        assert se.value.code == -1

    def test_add_student(self, capsys):
        # test missing course id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('add_student')
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # test missing student id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('add_student', course_id=self.course_id)
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        self._mock_add_student()
        cmd = self.form_command(
            'add_student',
            course_id=self.course_id,
            student_id=self.student_id,
            first_name='jane',
            last_name='doe',
            email='jd@mail.com',
        )
        nm.execute_command(cmd)
        out, err = capsys.readouterr()
        assert 'Successfully added/updated {}'.format(self.student_id) in out

    def test_add_students(self, capsys, tmp_path):
        self._mock_add_students()
        # test no course id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('add_students')
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # test no file
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('add_students', course_id=self.course_id)
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # test no non existing file
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command(
                'add_students', course_id=self.course_id, students_csv='dne'
            )
            nm.execute_command(cmd)

        assert se.type == SystemExit
        assert se.value.code == -1
        out, err = capsys.readouterr()
        assert 'The csv file you entered does not exist' in out

        cmd = self.form_command(
            'add_students',
            course_id=self.course_id,
            students_csv='students.csv',
        )
        nm.execute_command(cmd)
        out, err = capsys.readouterr()
        assert 'sid1 was sucessfuly added to math101' in out
        assert 'sid2 was sucessfuly added to math101' in out

    def test_add_instructor(self, capsys):
        self._mock_add_instructor()

        # test no course id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('add_instructor')
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # test no instructor id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('add_instructor', course_id=self.course_id)
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # test valid
        cmd = self.form_command(
            'add_instructor',
            course_id=self.course_id,
            instructor_id=self.instructor_id,
            first_name='john',
            last_name='doe',
            email='jd@mail.com',
        )
        nm.execute_command(cmd)
        out, err = capsys.readouterr()
        assert (
            'Successfully added {} as an instructor to {}'.format(
                self.instructor_id, self.course_id
            )
            in out
        )

    def test_remove_student(self, capsys):
        self._mock_remove_student()

        # test missing course id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('remove_student')
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # test missing student id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('remove_student', course_id=self.course_id)
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # test valid
        cmd = self.form_command(
            'remove_student',
            course_id=self.course_id,
            student_id=self.student_id,
        )
        nm.execute_command(cmd)
        out, err = capsys.readouterr()
        assert (
            'Successfully deleted {} from {}'.format(
                self.student_id, self.course_id
            )
            in out
        )

    def test_remove_instructor(self, capsys):
        self._mock_remove_instructor()

        # test missing course id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command('remove_instructor')
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # test missing student id
        with pytest.raises(SystemExit) as se:
            cmd = self.form_command(
                'remove_instructor', course_id=self.course_id
            )
            nm.execute_command(cmd)
        assert se.type == SystemExit
        assert se.value.code == -1

        # test valid
        cmd = self.form_command(
            'remove_instructor',
            course_id=self.course_id,
            instructor_id=self.instructor_id,
        )
        nm.execute_command(cmd)
        out, err = capsys.readouterr()
        assert (
            'Successfully deleted instructor {} from {}'.format(
                self.instructor_id, self.course_id
            )
            in out
        )

    def test_add_students_parsing(self, capsys):
        # test empty file
        new_file, filename = tempfile.mkstemp()
        with pytest.raises(SystemExit) as se:
            nm.add_students(self.course_id, filename, False)
        assert se.type == SystemExit
        assert se.value.code == -1
        out, err = capsys.readouterr()
        assert 'The csv file you entered is empty' in out

        # test missing a column
        new_file2, filename2 = tempfile.mkstemp()
        with open(filename2, 'w') as f:
            f.write('first_name,last_name,email')

        with pytest.raises(SystemExit) as se:
            nm.add_students(self.course_id, filename2, False)
        assert se.type == SystemExit
        assert se.value.code == -1
        out, err = capsys.readouterr()
        assert 'Missing column {} in {}.'.format('student_id', filename2) in out

        new_file3, filename3 = tempfile.mkstemp()
        with open(filename3, 'w') as f:
            f.write('student_id,first_name,last_name,email\n')
            f.write(',jane,doe,jd@mail.com')

        with pytest.raises(SystemExit) as se:
            nm.add_students(self.course_id, filename3, False)
        assert se.type == SystemExit
        assert se.value.code == -1
        out, err = capsys.readouterr()
        assert 'Student ID cannot be empty (row 1)' in out
