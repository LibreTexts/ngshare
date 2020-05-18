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


NGSHARE_URL = "http://127.0.0.1:12121/api"


class TestCourseManagement:
    course_id = 'math101'
    instructor = os.environ['USER']
    instructors = ['mi1', 'mi2']
    student_id = 'ms'

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
            'The request "%s" has not been mocked yet.', request.url
        )
        content.status_code = 404
        return ''

    def _get_student_info(self, request: PreparedRequest, context):
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
        return {
            "success": True,
            "status": [
                {"username": "sid1", "success": True},
                {"username": "sid2", "success": True},
            ],
        }

    def _mock_add_instructor_successful(self):
        url = '{}/instructor/{}/{}'.format(
            NGSHARE_URL, self.course_id, self.instructor
        )
        response = {"success": True}
        self.requests_mocker.post(url, json=response)

    def _mock_create_course_successful(self):
        url = '{}/course/{}'.format(NGSHARE_URL, self.course_id)
        response = {"success": True}
        self.requests_mocker.post(url, json=response)

    def _mock_create_course(self):
        url = '{}/course/{}'.format(NGSHARE_URL, self.course_id)

        if not self.course_created:
            response = {"success": True}
        else:
            response = {'success': False, 'message': 'Course already exists'}

        self.requests_mocker.post(url, json=response)

        if not self.course_created:
            self.course_created = True

    def _mock_add_student(self):
        url = '{}/student/{}/{}'.format(
            NGSHARE_URL, self.course_id, self.student_id
        )
        self.requests_mocker.post(url, json=self._get_student_info)

    def _mock_add_students(self):
        url = '{}/students/{}'.format(
            NGSHARE_URL, self.course_id, self.student_id
        )
        self.requests_mocker.post(url, json=self._get_students_info)

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
        assert " Successfully created {}\n".format(self.course_id) in out

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
        assert "Successfully added/updated {}".format(self.student_id) in out

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
