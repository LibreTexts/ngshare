'''
    ngshare Tornado server
'''

# pylint: disable=invalid-name
# pylint: disable=abstract-method
# pylint: disable=no-member
# pylint: disable=no-self-use
# pylint: disable=attribute-defined-outside-init
# pylint: disable=invalid-name

import os
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base, User, Course, Assignment, Submission, File

class MyHelpers:
    'Helper functions for database accesses'
    def json_error(self, msg, **kwargs):
        'Abstract method resolved in MyRequestHandler'
        raise NotImplementedError

    def strftime(self, dt):
        'Use API specified format to strftime'
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f %Z')

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
                self.json_error('Time format incorrect')

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

    def json_files_pack(self, file_list, list_only):
        'Generate JSON directory tree from a list of File objects'
        ans = []
        for i in file_list:
            if list_only:
                ans.append({
                    'path': i.filename,
                })
            else:
                ans.append({
                    'path': i.filename,
                    'content': base64.encodebytes(i.contents).decode(),
                })
        return ans

    def json_files_unpack(self, json_str, target):
        '''
            Generate a list of File objects from a JSON directory tree
            json_str: json object as string; raise error when None
            target: a list to put file objects in
        '''
        if json_str is None:
            self.json_error('Please supply files')
        try:
            json_obj = json.loads(json_str)
        except json.decoder.JSONDecodeError:
            self.json_error('Files cannot be JSON decoded')
        for i in json_obj:
            if not self.path_check(i['path']):
                self.json_error('Illegal path')
            try:
                content = base64.decodebytes(i['content'].encode())
            except binascii.Error:
                self.json_error('Content cannot be base64 decoded')
            target.append(File(i['path'], content))

    def find_course(self, course_id):
        'Return a Course object from id, or raise error'
        qry = self.db.query(Course)
        course = qry.filter(Course.id == course_id).one_or_none()
        if course is None:
            self.json_error('Course not found')
        return course

    def find_assignment(self, course, assignment_id):
        'Return an Assignment object from course and id, or raise error'
        assignment = self.db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.course == course).one_or_none()
        if assignment is None:
            self.json_error('Assignment not found')
        return assignment

    def find_course_user(self, course, student_id):
        'Return a student or instructor as User object from course and id'
        student = self.db.query(User).filter(
            User.id == student_id,
            User.taking.contains(course)).one_or_none()
        if student is None:
            self.json_error('Student not found')
        return student

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
            self.json_error('Submission not found')
        return submission

    def find_student_submission(self, assignment, student, timestamp):
        'Return the Submission object from timestamp etc'
        submission = self.find_student_submissions(assignment, student).filter(
            Submission.timestamp == timestamp).one_or_none()
        if submission is None:
            self.json_error('Submission not found')
        return submission

    # Auth APIs

    def is_course_student(self, course, user):
        'Return whether user is a student in the course'
        return course in user.taking

    def is_course_instructor(self, course, user):
        'Return whether user is an instructor in the course'
        return course in user.teaching

    def check_course_instructor(self, course):
        'Assert user is an instructor in the course'
        if not self.is_course_instructor(course, self.user):
            self.json_error('Permission denied (not course instructor)')

    def check_course_user(self, course):
        'Assert user is a student or an instructor in the course'
        if not self.is_course_instructor(course, self.user) and \
            not self.is_course_student(course, self.user):
            self.json_error('Permission denied (not related to course)')

class MyRequestHandler(HubAuthenticated, RequestHandler, MyHelpers):
    'Custom request handler for ngshare'
    def json_success(self, msg=None, **kwargs):
        'Return success as a JSON object'
        assert 'success' not in kwargs and 'message' not in kwargs
        resp = {'success': True, **kwargs}
        if msg is not None:
            resp['message'] = msg
        raise Finish(json.dumps(resp))

    def json_error(self, msg, **kwargs):
        'Return error as a JSON object'
        assert 'success' not in kwargs and 'message' not in kwargs
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
        pwd = os.path.dirname(os.path.realpath(__file__))
        file_name = os.path.join(pwd, 'home.html')
        self.write(open(file_name).read())

class Favicon(MyRequestHandler):
    '/api/favicon.ico'
    @authenticated
    def get(self):
        'Serve favicon'
        pwd = os.path.dirname(os.path.realpath(__file__))
        file_name = os.path.join(pwd, 'favicon.ico')
        self.write(open(file_name, 'rb').read())

class ListCourses(MyRequestHandler):
    '/api/courses'
    @authenticated
    def get(self):
        'List all available courses the user is taking or teaching (anyone)'
        courses = set()
        for i in self.user.teaching:
            courses.add(i.id)
        for i in self.user.taking:
            courses.add(i.id)
        self.json_success(courses=sorted(courses))

class AddCourse(MyRequestHandler):
    '/api/course/<course_id>'
    @authenticated
    def post(self, course_id):
        'Add a course (anyone)'
        if self.db.query(Course).filter(Course.id == course_id).one_or_none():
            self.json_error('Course already exists')
        course = Course(course_id, self.user)
        self.db.add(course)
        self.db.commit()
        self.json_success()

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
            self.json_error('Assignment already exists')
        assignment = Assignment(assignment_id, course)
        files = self.get_argument('files', None)
        self.json_files_unpack(files, assignment.files)
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
                # TODO: "notebooks": [],
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
                # TODO: "notebooks": [],
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
        self.json_success()

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
        submission = self.find_student_latest_submission(assignment, student)
        list_only = self.get_argument('list_only', 'false') == 'true'
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
            self.json_error('Please supply timestamp')
        submission = self.find_student_submission(assignment, student,
                                                  timestamp)
        submission.feedbacks.clear()
        # TODO: does this automatically remove the files?
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
            self.json_error('Please supply timestamp')
        submission = self.find_student_submission(assignment, student,
                                                  timestamp)
        list_only = self.get_argument('list_only', 'false') == 'true'
        files = self.json_files_pack(submission.feedbacks, list_only)
        self.json_success(files=files,
                          timestamp=self.strftime(submission.timestamp))

class Test404Handler(RequestHandler):
    '404 handler'
    def get(self):
        'Disable 404 page'
        self.write("This would have 404'd. Double check URL.\n")
        self.write(json.dumps(dict(os.environ), indent=1, sort_keys=True))
        self.write("\n"+self.request.uri+"\n"+self.request.path+"\n")

def main():
    'Main function'
    parser = argparse.ArgumentParser(
        description='ngshare, a REST API nbgrader exchange')
    parser.add_argument(
        '--jupyterhub_api_url',
        help='Override the JUPYTERHUB_API_URL environment variable')
    args = parser.parse_args()
    if args.jupyterhub_api_url is not None:
        os.environ['JUPYTERHUB_API_URL'] = args.jupyterhub_api_url

    prefix = os.environ['JUPYTERHUB_SERVICE_PREFIX']
    app = Application(
        [
            (prefix, HomePage),
            (prefix + 'favicon.ico', Favicon),
            (prefix + 'courses', ListCourses),
            (prefix + 'course/([^/]+)', AddCourse),
            (prefix + 'assignments/([^/]+)', ListAssignments),
            (prefix + 'assignment/([^/]+)/([^/]+)', DownloadReleaseAssignment),
            (prefix + 'submissions/([^/]+)/([^/]+)', ListSubmissions),
            (prefix + 'submissions/([^/]+)/([^/]+)/([^/]+)',
             ListStudentSubmissions),
            (prefix + 'submission/([^/]+)/([^/]+)', SubmitAssignment),
            (prefix + 'submission/([^/]+)/([^/]+)/([^/]+)', DownloadAssignment),
            (prefix + 'feedback/([^/]+)/([^/]+)/([^/]+)',
             UploadDownloadFeedback),
            (r'.*', Test404Handler),
        ],
        autoreload=True
    )

    engine = create_engine('sqlite:////srv/ngshare/ngshare.db')
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    app.db_session = sessionmaker(bind=engine)

    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    # Must listen on all interfaces for proxy
    http_server.listen(url.port, '0.0.0.0')

    IOLoop.current().start()

if __name__ == '__main__':
    main()
