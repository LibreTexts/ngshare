'''
    ngshare Tornado server
'''

from database.database import Base, User, Course, Assignment, Submission, File
import json
import os
import argparse
from urllib.parse import urlparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import authenticated
from tornado.web import RequestHandler

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
        0/0

    def find_course(self, course_id):
        'Return a Course object from id, or raise error'
        qry = self.db.query(Course)
        course = qry.filter(Course.id == course_id).one_or_none()
        if course is None:
            self.json_error('Course not found')
        return course

    def is_course_student(self, course, user) :
        'Return whether user is a student in the course'
        return course in user.taking

    def is_course_instructor(self, course, user) :
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
        self.finish(json.dumps(resp))

    def json_error(self, msg, **kwargs):
        'Return error as a JSON object'
        assert 'success' not in kwargs and 'message' not in kwargs
        self.finish(json.dumps({'success': False, 'message': msg, **kwargs}))

    def prepare(self):
        'Provide a db object'
        self.db = Session()
        self.user = User.from_jupyterhub_user(self.get_current_user(), self.db)

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
        self.check_course_related(course, self.user)
        assignments = course.assignments
        self.json_success(assignments=list(map(lambda x: x.id, assignments)))

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

    app = Application(
        [
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'],
             HomePage),
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + 'favicon.ico',
             Favicon),
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + 'courses',
             ListCourses),
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + 'course/([^/]+)',
             AddCourse),
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + 'assignments/([^/]+)',
             ListAssignments),
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
