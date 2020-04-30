'''
    ngshare Tornado server
'''

# pylint: disable=abstract-method
# pylint: disable=attribute-defined-outside-init
# pylint: disable=invalid-name
# pylint: disable=invalid-name
# pylint: disable=no-member
# pylint: disable=no-self-use
# pylint: disable=too-many-arguments
# pylint: disable=too-many-public-methods

import os
import uuid
import json
import argparse
import base64
import binascii
import datetime
from urllib.parse import urlparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import (Application, authenticated, RequestHandler, Finish,
                         MissingArgumentError)
from jupyterhub.services.auth import HubAuthenticated
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from database.database import (Base, User, Course, Assignment, Submission, File,
                               InstructorAssociation, StudentAssociation)
from database.test_database import clear_db, init_db, dump_db

class MyHelpers:
    'Helper functions for database accesses'
    def json_error(self, code, msg, **kwargs):
        'Abstract method resolved in MyRequestHandler'
        raise NotImplementedError

    def strftime(self, dt):
        'Use API specified format to strftime'
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f %Z').strip()

    def strptime(self, string):
        'Use API specified format to strptime'
        try:
            return datetime.datetime.strptime(string,
                                              '%Y-%m-%d %H:%M:%S.%f %Z')
        except ValueError:
            try:
                return datetime.datetime.strptime(string.strip(),
                                                  '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                self.json_error(400, 'Time format incorrect')

    def path_check(self, pathname):
        '''
            Return whether a pathname (for file, in director tree) is safe
            Current policy:
                Not empty
                os.path.abspath resolves to a child address
                Path does not contain ('.', '..', '', '/')
            Note: os.path.abspath is used instead of os.path.realpath to prevent
             symbolic link issues, because the file is not on server
            Note: os.path.abspath is not 100% safe
            Note: currently only using Linux pathname conventions
        '''
        if not pathname:
            return False
        path = pathname
        while path:
            path, name = os.path.split(path)
            if name in ('.', '..', '', '/'):
                return False
        working = os.path.abspath('.')
        target = os.path.abspath(pathname)
        if os.path.commonpath([working, target]) != working:
            return False
        return True

    def filename_create(self, filename):
        'Create a file name for storage; trying to follow extension'
        ext = os.path.splitext(filename)[1]
        if len(ext) > 10:
            ext = ''
        return str(uuid.uuid4()) + ext

    def json_files_pack(self, file_list, list_only):
        'Generate JSON directory tree from a list of File objects'
        ans = []
        for i in file_list:
            entry = {
                'path': i.filename,
                'checksum': i.checksum,
            }
            if not list_only:
                storage_path = self.application.storage_path
                actual_path = os.path.join(storage_path, i.actual_name)
                content = open(actual_path, 'rb').read()
                entry['content'] = base64.encodebytes(content).decode()
            ans.append(entry)
        return ans

    def json_files_unpack(self, json_str, target):
        '''
            Generate a list of File objects from a JSON directory tree
            json_str: json object as string; raise error when None
            target: a list to put file objects in
        '''
        if json_str is None:
            self.json_error(400, 'Please supply files')
        try:
            json_obj = json.loads(json_str)
        except json.decoder.JSONDecodeError:
            self.json_error(400, 'Files cannot be JSON decoded')
        content_list = []
        for i in json_obj:
            if not self.path_check(i['path']):
                self.json_error(400, 'Illegal path')
            try:
                content = base64.decodebytes(i['content'].encode())
            except binascii.Error:
                self.json_error(400, 'Content cannot be base64 decoded')
            target.append(File(i['path'], content))
            content_list.append(content)
        # Commit files
        storage_path = self.application.storage_path
        os.makedirs(storage_path, exist_ok=True)
        for file_obj, content in zip(target, content_list):
            f = None
            for i in range(10):
                actual_name = self.filename_create(file_obj.filename)
                try:
                    f = open(os.path.join(storage_path, actual_name), 'xb')
                    break
                except FileExistsError:
                    pass
            if f is None:
                raise self.json_error(500, 'Internal server error')
            f.write(content)
            f.close()
            file_obj.actual_name = actual_name

    def find_or_create_user(self, user_id):
        'Return a User object from id; create if not found'
        user = self.db.query(User).filter(User.id == user_id).one_or_none()
        if user is None:
            user = User(user_id)
            self.db.add(user)
            self.db.commit()
        return user

    def find_course(self, course_id):
        'Return a Course object from id, or raise error'
        qry = self.db.query(Course)
        course = qry.filter(Course.id == course_id).one_or_none()
        if course is None:
            self.json_error(404, 'Course not found')
        return course

    def find_assignment(self, course, assignment_id):
        'Return an Assignment object from course and id, or raise error'
        assignment = self.db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.course == course).one_or_none()
        if assignment is None:
            self.json_error(404, 'Assignment not found')
        return assignment

    def find_course_instructor(self, course, instructor_id):
        'Return a instructor as User object from course and id'
        instructor = self.db.query(User).filter(
            User.id == instructor_id,
            User.teaching.contains(course)).one_or_none()
        if instructor is None:
            self.json_error(404, 'Instructor not found')
        return instructor

    def find_course_student(self, course, student_id):
        'Return a student as User object from course and id'
        student = self.db.query(User).filter(
            User.id == student_id,
            User.taking.contains(course)).one_or_none()
        if student is None:
            self.json_error(404, 'Student not found')
        return student

    def find_course_user(self, course, user_id):
        'Return a student or instructor as User object from course and id'
        user = self.db.query(User).filter(
            User.id == user_id,
            or_(User.taking.contains(course),
                User.teaching.contains(course))).one_or_none()
        if user is None:
            self.json_error(404, 'Student not found')
        return user

    def find_student_submissions(self, assignment, student):
        'Return a list of Submission objects from assignment and student'
        return self.db.query(Submission).filter(
            Submission.assignment == assignment,
            Submission.student == student)

    def find_student_latest_submission(self, assignment, student):
        'Return the latest Submission object from assignment and studnet'
        submission = self.find_student_submissions(assignment, student) \
                    .order_by(Submission.timestamp.desc()).first()
        if submission is None:
            self.json_error(404, 'Submission not found')
        return submission

    def find_student_submission(self, assignment, student, timestamp):
        'Return the Submission object from timestamp etc'
        submission = self.find_student_submissions(assignment, student).filter(
            Submission.timestamp == timestamp).one_or_none()
        if submission is None:
            self.json_error(404, 'Submission not found')
        return submission

    # User management

    def wrap_instructor_info(self, user, course):
        'Return dict of instructor info (full name, email, etc)'
        association = InstructorAssociation.find(self.db, user, course)
        if association is None: # Error in data integrity
            return {
                'username': user.id,
                'first_name': None,
                'last_name': None,
                'email': None,
            }
        return {
            'username': user.id,
            'first_name': association.first_name,
            'last_name': association.last_name,
            'email': association.email,
        }

    def wrap_student_info(self, user, course):
        'Return dict of student info (full name, email, etc)'
        association = StudentAssociation.find(self.db, user, course)
        if association is None: # Error in data integrity
            return {
                'username': user.id,
                'first_name': None,
                'last_name': None,
                'email': None,
            }
        return {
            'username': user.id,
            'first_name': association.first_name,
            'last_name': association.last_name,
            'email': association.email,
        }

    # Auth APIs

    def is_root(self):
        'Return whether user is root user'
        return self.user.id in self.application.root

    def is_course_student(self, course, user):
        'Return whether user is a student in the course'
        return course in user.taking

    def is_course_instructor(self, course, user):
        'Return whether user is an instructor in the course'
        return course in user.teaching

    def check_root(self):
        'Assert user is root user'
        if not self.is_root():
            msg = 'Permission denied'
            if self.application.debug:
                msg += ' (not root)'
            self.json_error(403, msg)

    def check_course_instructor(self, course):
        'Assert user is an instructor in the course, or root'
        if not self.is_root() and \
            not self.is_course_instructor(course, self.user):
            msg = 'Permission denied'
            if self.application.debug:
                msg += ' (not course instructor)'
            self.json_error(403, msg)

    def check_course_user(self, course):
        'Assert user is a student or an instructor in the course, or root'
        if not self.is_root() and \
            not self.is_course_instructor(course, self.user) and \
            not self.is_course_student(course, self.user):
            msg = 'Permission denied'
            if self.application.debug:
                msg += ' (not related to course)'
            self.json_error(403, msg)

class MyRequestHandler(HubAuthenticated, RequestHandler, MyHelpers):
    'Custom request handler for ngshare'
    def json_success(self, msg=None, **kwargs):
        'Return success as a JSON object'
        assert 'success' not in kwargs and 'message' not in kwargs
        resp = {'success': True, **kwargs}
        if msg is not None:
            resp['message'] = msg
        raise Finish(json.dumps(resp))

    def json_error(self, code, msg, **kwargs):
        'Return error as a JSON object'
        assert 'success' not in kwargs and 'message' not in kwargs
        self.set_status(code)
        raise Finish(json.dumps({'success': False, 'message': msg, **kwargs}))

    def prepare(self):
        'Provide a db object'
        self.db = self.application.db_session()
        current_user = self.get_current_user()
        if current_user is not None:
            self.user = User.from_jupyterhub_user(current_user, self.db)
        else:
            self.user = None

    def on_finish(self):
        self.db.close()

class HomePage(MyRequestHandler):
    '/api/'
    @authenticated
    def get(self):
        'Display an HTML page for debugging'
        self.render('home.html', debug=self.application.debug or self.is_root(),
                    vngshare=self.application.vngshare)

class Static(MyRequestHandler):
    '/api/favicon.ico, /api/masonry.min.js'
    @authenticated
    def get(self, name):
        'Static files'
        pwd = os.path.dirname(os.path.realpath(__file__))
        file_name = os.path.join(pwd, name)
        self.write(open(file_name, 'rb').read())

class ListCourses(MyRequestHandler):
    '/api/courses'
    @authenticated
    def get(self):
        '''
            List all available courses the user is taking or teaching. (anyone)
            List all courses in ngshare. (root)
        '''
        courses = set()
        if self.is_root():
            for i in self.db.query(Course).all():
                courses.add(i.id)
        else:
            for i in self.user.teaching:
                courses.add(i.id)
            for i in self.user.taking:
                courses.add(i.id)
        self.json_success(courses=sorted(courses))

class AddCourse(MyRequestHandler):
    '/api/course/<course_id>'
    @authenticated
    def post(self, course_id):
        'Add a course (root)'
        self.check_root()
        if self.db.query(Course).filter(Course.id == course_id).one_or_none():
            self.json_error(409, 'Course already exists')
        course = Course(course_id, self.user)
        self.db.add(course)
        self.db.commit()
        self.json_success()

class ManageInstructor(MyRequestHandler):
    '/api/instructor/<course_id>/<instructor_id>'
    @authenticated
    def post(self, course_id, instructor_id):
        '''
            Add or update a course instructor. (root)
            Update self full name or email. (instructors)
        '''
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        instructor = self.find_or_create_user(instructor_id)
        first_name = self.get_argument('first_name', None)
        if first_name is None:
            self.json_error(400, 'Please supply first name')
        last_name = self.get_argument('last_name', None)
        if last_name is None:
            self.json_error(400, 'Please supply last name')
        email = self.get_argument('email', None)
        if email is None:
            self.json_error(400, 'Please supply email')
        if instructor in course.students:
            if not self.is_root():
                self.json_error(400, 'Permission denied'
                                ' (cannot modify instructors)')
            course.students.remove(instructor)
        if instructor not in course.instructors:
            if not self.is_root():
                self.json_error(400, 'Permission denied'
                                ' (cannot modify instructors)')
            course.instructors.append(instructor)
        if not self.is_root() and instructor.id != self.user.id:
            self.json_error(400, 'Permission denied'
                            ' (cannot modify other instructors)')
        association = InstructorAssociation.find(self.db, instructor, course)
        association.first_name = first_name
        association.last_name = last_name
        association.email = email
        self.db.commit()
        self.json_success()

    @authenticated
    def get(self, course_id, instructor_id):
        'Get information about a course instructor. (instructors+students)'
        course = self.find_course(course_id)
        self.check_course_user(course)
        instructor = self.find_course_instructor(course, instructor_id)
        ans = self.wrap_instructor_info(instructor, course)
        self.json_success(**ans)

    @authenticated
    def delete(self, course_id, instructor_id):
        'Remove a course instructor (root)'
        self.check_root()
        course = self.find_course(course_id)
        instructor = self.find_course_instructor(course, instructor_id)
        course.instructors.remove(instructor)
        self.db.commit()
        self.json_success()

class ListInstructors(MyRequestHandler):
    '/api/instructors/<course_id>/'
    @authenticated
    def get(self, course_id):
        'Get information about all course instructors. (instructors+students)'
        course = self.find_course(course_id)
        self.check_course_user(course)
        ans = []
        for instructor in course.instructors:
            ans.append(self.wrap_instructor_info(instructor, course))
        self.json_success(instructors=ans)

class ManageStudent(MyRequestHandler):
    '/api/student/<course_id>/<student_id>'
    @authenticated
    def post(self, course_id, student_id):
        'Add or update a student. (instructors only)'
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        student = self.find_or_create_user(student_id)
        first_name = self.get_argument('first_name', None)
        if first_name is None:
            self.json_error(400, 'Please supply first name')
        last_name = self.get_argument('last_name', None)
        if last_name is None:
            self.json_error(400, 'Please supply last name')
        email = self.get_argument('email', None)
        if email is None:
            self.json_error(400, 'Please supply email')
        if student in course.instructors:
            self.json_error(409, 'Cannot add instructor as student')
        if student not in course.students:
            course.students.append(student)
        association = StudentAssociation.find(self.db, student, course)
        association.first_name = first_name
        association.last_name = last_name
        association.email = email
        self.db.commit()
        self.json_success()

    @authenticated
    def get(self, course_id, student_id):
        '''
            Get information about a student.
            (instructors+student with same student_id)
        '''
        course = self.find_course(course_id)
        if self.user.id != student_id:
            self.check_course_instructor(course)
        student = self.find_course_student(course, student_id)
        ans = self.wrap_student_info(student, course)
        self.json_success(**ans)

    @authenticated
    def delete(self, course_id, student_id):
        'Remove a student (instructors only)'
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        student = self.find_course_student(course, student_id)
        course.students.remove(student)
        self.db.commit()
        self.json_success()

class ListStudents(MyRequestHandler):
    '/api/students/<course_id>/'
    @authenticated
    def post(self, course_id):
        'Add or update students. (instructors only)'
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        students_str = self.get_argument('students', None)
        # Check request format
        if not students_str:
            self.json_error(400, 'Please supply students')
        try:
            students = json.loads(students_str)
        except json.decoder.JSONDecodeError:
            self.json_error(400, 'Students cannot be JSON decoded')
        if type(students) != list:
            self.json_error(400, 'Incorrect request format')
        if not students:
            self.json_error(400, 'Please supply students')
        for i in students:
            if type(i) is not dict or \
                type(i.get('username')) is not str or \
                type(i.get('first_name')) is not str or \
                type(i.get('last_name')) is not str or \
                type(i.get('email')) is not str:
                self.json_error(400, 'Incorrect request format')
        # Commit
        ans = []
        for i in students:
            student = self.find_or_create_user(i['username'])
            if student in course.instructors:
                ans.append({
                    'username': i['username'],
                    'success': False,
                    'message': 'Cannot add instructor as student',
                })
                continue
            if student not in course.students:
                course.students.append(student)
            association = StudentAssociation.find(self.db, student, course)
            association.first_name = i['first_name']
            association.last_name = i['last_name']
            association.email = i['email']
            ans.append({
                'username': i['username'],
                'success': True,
            })
        self.db.commit()
        self.json_success(status=ans)

    @authenticated
    def get(self, course_id):
        'Get information about all course students. (instructors only)'
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        ans = []
        for student in course.students:
            ans.append(self.wrap_student_info(student, course))
        self.json_success(students=ans)

class ListAssignments(MyRequestHandler):
    '/api/assignments/<course_id>'
    @authenticated
    def get(self, course_id):
        'List all assignments for a course (students+instructors)'
        course = self.find_course(course_id)
        self.check_course_user(course)
        assignments = course.assignments
        self.json_success(assignments=list(map(lambda x: x.id, assignments)))

class DownloadReleaseAssignment(MyRequestHandler):
    '/api/assignment/<course_id>/<assignment_id>'
    def get(self, course_id, assignment_id):
        'Download a copy of an assignment (students+instructors)'
        course = self.find_course(course_id)
        self.check_course_user(course)
        assignment = self.find_assignment(course, assignment_id)
        list_only = self.get_argument('list_only', 'false') == 'true'
        files = self.json_files_pack(assignment.files, list_only)
        self.json_success(files=files)

    def post(self, course_id, assignment_id):
        'Release an assignment (instructors only)'
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        if self.db.query(Assignment).filter(
                Assignment.id == assignment_id,
                Assignment.course == course).one_or_none():
            self.json_error(409, 'Assignment already exists')
        assignment = Assignment(assignment_id, course)
        files = self.get_argument('files', None)
        self.json_files_unpack(files, assignment.files)
        self.db.commit()
        self.json_success()

    def delete(self, course_id, assignment_id):
        'Remove an assignment (instructors only)'
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        assignment = self.find_assignment(course, assignment_id)
        assignment.delete(self.db)
        self.db.commit()
        self.json_success()

class ListSubmissions(MyRequestHandler):
    '/api/submissions/<course_id>/<assignment_id>'
    def get(self, course_id, assignment_id):
        '''
            List all submissions for an assignment from all students
             (instructors only)
        '''
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        assignment = self.find_assignment(course, assignment_id)
        submissions = []
        for submission in assignment.submissions:
            submissions.append({
                'student_id': submission.student.id,
                'timestamp': self.strftime(submission.timestamp),
            })
        self.json_success(submissions=submissions)

class ListStudentSubmissions(MyRequestHandler):
    '/api/submissions/<course_id>/<assignment_id>/<student_id>'
    def get(self, course_id, assignment_id, student_id):
        '''
            List all submissions for an assignment from a particular student
             (instructors+students,
              students restricted to their own submissions)
        '''
        course = self.find_course(course_id)
        if self.user.id != student_id:
            self.check_course_instructor(course)
        assignment = self.find_assignment(course, assignment_id)
        student = self.find_course_user(course, student_id)
        submissions = []
        for submission in self.find_student_submissions(assignment, student):
            submissions.append({
                'student_id': submission.student.id,
                'timestamp': self.strftime(submission.timestamp),
            })
        self.json_success(submissions=submissions)

class SubmitAssignment(MyRequestHandler):
    '/api/submission/<course_id>/<assignment_id>'
    def post(self, course_id, assignment_id):
        'Submit a copy of an assignment (students+instructors)'
        course = self.find_course(course_id)
        self.check_course_user(course)
        assignment = self.find_assignment(course, assignment_id)
        submission = Submission(self.user, assignment)
        files = self.get_body_argument('files', None)
        self.json_files_unpack(files, submission.files)
        self.db.commit()
        self.json_success(timestamp=self.strftime(submission.timestamp))

class DownloadAssignment(MyRequestHandler):
    '/api/submission/<course_id>/<assignment_id>/<student_id>'
    def get(self, course_id, assignment_id, student_id):
        '''
            Download a student's submitted assignment (instructors only)
            TODO: maybe allow student to see their own submissions?
        '''
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        assignment = self.find_assignment(course, assignment_id)
        student = self.find_course_user(course, student_id)
        list_only = self.get_argument('list_only', 'false') == 'true'
        timestamp = self.get_argument('timestamp', '')
        if not timestamp:
            submission = self.find_student_latest_submission(assignment,
                                                             student)
        else:
            submission = self.find_student_submission(assignment, student,
                                                      timestamp)
        files = self.json_files_pack(submission.files, list_only)
        self.json_success(files=files,
                          timestamp=self.strftime(submission.timestamp))

class UploadDownloadFeedback(MyRequestHandler):
    '/api/feedback/<course_id>/<assignment_id>/<student_id>'
    def post(self, course_id, assignment_id, student_id):
        '''
            POST /api/feedback/<course_id>/<assignment_id>/<student_id>
            Upload feedback on a student's assignment (instructors only)
        '''
        course = self.find_course(course_id)
        self.check_course_instructor(course)
        assignment = self.find_assignment(course, assignment_id)
        student = self.find_course_user(course, student_id)
        try:
            timestamp = self.strptime(self.get_body_argument('timestamp'))
        except MissingArgumentError:
            self.json_error(400, 'Please supply timestamp')
        submission = self.find_student_submission(assignment, student,
                                                  timestamp)
        for file_obj in submission.feedbacks:
            file_obj.delete(self.db)
        submission.feedbacks.clear()
        files = self.get_body_argument('files', None)
        self.json_files_unpack(files, submission.feedbacks)
        self.db.commit()
        self.json_success()

    def get(self, course_id, assignment_id, student_id):
        '''
            GET /api/feedback/<course_id>/<assignment_id>/<student_id>
            Download feedback on a student's assignment
             (instructors+students, students restricted to own submissions)
        '''
        course = self.find_course(course_id)
        if self.user.id != student_id:
            self.check_course_instructor(course)
        assignment = self.find_assignment(course, assignment_id)
        student = self.find_course_user(course, student_id)
        try:
            timestamp = self.strptime(self.get_query_argument('timestamp'))
        except MissingArgumentError:
            self.json_error(400, 'Please supply timestamp')
        submission = self.find_student_submission(assignment, student,
                                                  timestamp)
        list_only = self.get_argument('list_only', 'false') == 'true'
        files = self.json_files_pack(submission.feedbacks, list_only)
        self.json_success(files=files,
                          timestamp=self.strftime(submission.timestamp))

class InitDatabase(MyRequestHandler):
    '/initialize-Data6ase'
    @authenticated
    def get(self):
        'Initialize database similar to in vserver'
        # Dangerous: do not use in production
        action = self.get_argument('action', None)
        if not self.application.debug:
            if not self.is_root() or action != 'dump':
                self.json_error(403, 'Debug mode is off')
        if action == 'clear':
            clear_db(self.db, self.application.storage_path)
            self.json_success('done')
        elif action == 'init':
            init_db(self.db, self.application.storage_path)
            self.json_success('done')
        elif action == 'dump':
            result = dump_db(self.db)
            if self.get_argument('human-readable', 'false') != 'true':
                self.json_success(**result)
            ans = []
            for key, value in result.items():
                if value:
                    thead = list(value[0])
                else:
                    thead = ['']
                tbody = []
                for line in value:
                    tbody.append(list(map(line.__getitem__, thead)))
                ans.append({
                    'header': key,
                    'thead': thead,
                    'tbody': tbody,
                })
            self.render('dump.html', tables=ans)
        else:
            self.json_error(400, 'action should be clear, init, or dump')

class NotFoundHandler(RequestHandler):
    '404 handler'
    def get(self):
        'Disable 404 page'
        self.write("<h1>404 Not Found</h1>\n")
        if not self.application.debug:
            return
        self.write(json.dumps(dict(os.environ), indent=1, sort_keys=True))
        self.write('\n' + self.request.uri + '\n' + self.request.path + '\n')

class MyApplication(Application):
    'Custom application for ngshare'
    def __init__(self, prefix, db_url, storage_path, debug=False,
                 root=[], autoreload=True):
        handlers = [
            (prefix, HomePage),
            (prefix + r'(favicon\.ico)', Static),
            (prefix + r'(masonry\.min\.js)', Static),
            (prefix + 'courses', ListCourses),
            (prefix + 'course/([^/]+)', AddCourse),
            (prefix + 'instructor/([^/]+)/([^/]+)', ManageInstructor),
            (prefix + 'instructors/([^/]+)', ListInstructors),
            (prefix + 'student/([^/]+)/([^/]+)', ManageStudent),
            (prefix + 'students/([^/]+)', ListStudents),
            (prefix + 'assignments/([^/]+)', ListAssignments),
            (prefix + 'assignment/([^/]+)/([^/]+)', DownloadReleaseAssignment),
            (prefix + 'submissions/([^/]+)/([^/]+)', ListSubmissions),
            (prefix + 'submissions/([^/]+)/([^/]+)/([^/]+)',
             ListStudentSubmissions),
            (prefix + 'submission/([^/]+)/([^/]+)', SubmitAssignment),
            (prefix + 'submission/([^/]+)/([^/]+)/([^/]+)', DownloadAssignment),
            (prefix + 'feedback/([^/]+)/([^/]+)/([^/]+)',
             UploadDownloadFeedback),
            (prefix + 'initialize-Data6ase', InitDatabase),
        ]
        handlers.append((r'.*', NotFoundHandler))
        super(MyApplication, self).__init__(handlers, debug=debug,
                                            autoreload=autoreload)
        # Connect Database
        engine = create_engine(db_url)
        Base.metadata.bind = engine
        Base.metadata.create_all(engine)
        self.db_session = sessionmaker(bind=engine)
        self.storage_path = storage_path
        self.debug = debug
        self.vngshare = False
        self.root = root

def main():
    'Main function'
    parser = argparse.ArgumentParser(
        description='ngshare, a REST API nbgrader exchange')
    parser.add_argument('--jupyterhub_api_url',
                        help='override $JUPYTERHUB_API_URL')
    parser.add_argument('--debug', action='store_true', help='enable debug')
    parser.add_argument('--database', help='database url',
                        default='sqlite:////srv/ngshare/ngshare.db')
    parser.add_argument('--storage', help='path to store files',
                        default='/srv/ngshare/files/')
    parser.add_argument('--root', help='root user ids (comma splitted)',
                        default='root')
    args = parser.parse_args()
    if args.jupyterhub_api_url is not None:
        os.environ['JUPYTERHUB_API_URL'] = args.jupyterhub_api_url

    prefix = os.environ['JUPYTERHUB_SERVICE_PREFIX']
    app = MyApplication(prefix, args.database, args.storage,
                        root=args.root.split(','), debug=args.debug)

    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    # Must listen on all interfaces for proxy
    http_server.listen(url.port, '0.0.0.0')

    IOLoop.current().start()

if __name__ == '__main__':
    main()
