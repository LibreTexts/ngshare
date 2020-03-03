'''
    ngshare Tornado server
'''

from database.database import Base, User, Course, Assignment, Submission, File
import json
import os
import argparse
from urllib.parse import urlparse

import base64, binascii, datetime

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, authenticated, RequestHandler, Finish

from jupyterhub.services.auth import HubAuthenticated

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:////srv/ngshare/ngshare.db')
Base.metadata.bind = engine
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# pylint: disable=invalid-name
# pylint: disable=abstract-method

class MyHelpers:
    'Helper functions for database accesses'
    def strftime(self, dt):
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f %Z')

    def strptime(self, string):
        0/0

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
        'Generate JSON file list (directory tree) from a list of File objects'
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
            Generate a list of File objects from a JSON file list (directory tree)
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

    def find_course_student(self, course, student_id):    
        'Return a Student object from course and id, or raise error'
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
        'Return the latest Submission object from assignment and studnet, or error'
        submission = self.find_student_submissions(assignment, student) \
                    .order_by(Submission.timestamp.desc()).first()
        if submission is None:
            self.json_error('Submission not found')
        return submission

    def find_student_submission(self, assignment, student, timestamp, random_str):
        'Return the Submission object from timestamp etc, or error'
        submission = self.find_student_submissions(assignment, student).filter(
                    Submission.timestamp==timestamp,
                    Submission.random==random_str).one_or_none()
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

    def check_course_student(self, course, user):
        'Assert user is a student in the course'
        if not self.is_course_student(course, user):
            self.json_error('Permission denied (not course student)')

    def check_course_instructor(self, course, user):
        'Assert user is an instructor in the course'
        if not self.is_course_instructor(course, user):
            self.json_error('Permission denied (not course instructor)')

    def check_course_related(self, course, user):
        'Assert user is a student or an instructor in the course'
        if not self.is_course_instructor(course, user) and \
            not self.is_course_student(course, user):
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
        self.db = Session()
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

class InitDatabase(MyRequestHandler):
    @authenticated
    def get(self):
        # Dangerous: do not use in production
        db = self.db
        db.query(User).delete()
        db.query(Course).delete()
        db.query(Assignment).delete()
        db.query(Submission).delete()
        db.query(File).delete()
        db.commit()
        uk = User('kevin')
        ua = User('abigail')
        ul = User('lawrence')
        ue = User('eric')
        course1 = Course('course1', uk)
        course2 = Course('course2', ua)
        db.add(course1)
        db.add(course2)
        course1.students.append(ul)
        course2.students.append(ue)
        aa = Assignment('assignment2a', course2)
        ab = Assignment('assignment2b', course2)
        ac = Assignment('challenge', course1)
        db.add(aa)
        db.add(ab)
        db.add(ac)
        s1 = Submission(ul, ac)
        s2 = Submission(ul, ac)
        s1.timestamp = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
        s1.random = '12345678-90ab-cdef-0123-456789abcdef'
        db.add(s1)
        db.add(s2)
        aa.files.append(File('file0', b'00000'))
        ab.files.append(File('file1', b'11111'))
        ac.files.append(File('file2', b'22222'))
        s1.files.append(File('file3', b'33333'))
        s2.files.append(File('file4', b'44444'))
        s1.feedbacks.append(File('file5', b'55555'))
        db.commit()
        self.json_success('done')

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
        self.check_course_related(course, self.user)
        assignments = course.assignments
        self.json_success(assignments=list(map(lambda x: x.id, assignments)))

class DownloadReleaseAssignment(MyRequestHandler):
    '/api/assignment/<course_id>/<assignment_id>'
    def get(self, course_id, assignment_id):
        'Download a copy of an assignment (students+instructors)'
        course = self.find_course(course_id)
        self.check_course_related(course, self.user)
        assignment = self.find_assignment(course, assignment_id)
        list_only = self.get_argument('list_only', 'false') == 'true'
        files = self.json_files_pack(assignment.files, list_only)
        self.json_success(files=files)

    def post(self, course_id, assignment_id):
        'Release an assignment (instructors only)'
        course = self.find_course(course_id)
        self.check_course_instructor(course, self.user)
        if self.db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.course == course).one_or_none():
            self.json_error('Assignment already exists')
        assignment = Assignment(assignment_id, course)
        files = self.get_argument('files', None)
        self.json_files_unpack(files, assignment.files)
        self.db.commit()
        self.json_success()

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
            (prefix + 'initialize-Data6ase', InitDatabase),
            (r'.*', Test404Handler),
        ],
        autoreload=True
    )

    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    # Must listen on all interfaces for proxy
    http_server.listen(url.port, '0.0.0.0')

    IOLoop.current().start()

if __name__ == '__main__':
    main()
