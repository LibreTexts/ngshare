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

class MyRequestHandler(RequestHandler):
    '''
        Custom request handler for ngshare
    '''
    def json_success(self, msg=None, **kwargs):
        '''
            Return success as a JSON object
        '''
        assert 'success' not in kwargs and 'message' not in kwargs
        resp = {'success': True, **kwargs}
        if msg is not None:
            resp['message'] = msg
        self.write(json.dumps(resp))

class ListCourses(HubAuthenticated, MyRequestHandler, RequestHandler):
    '/api/courses'
    @authenticated
    def get(self):
        'List all available courses the user is taking or teaching (anyone)'
        db = Session()
        user = User.from_jupyterhub_user(self.get_current_user(), db)
        courses = set()
        for i in user.teaching:
            courses.add(i.id)
        for i in user.taking:
            courses.add(i.id)
        return self.json_success(courses=sorted(courses))

class TestCreateCourseHandler(HubAuthenticated, RequestHandler):
    @authenticated
    def post(self, courseid):
        db = Session()
        user = User.from_jupyterhub_user(self.get_current_user(), db)
        if db.query(Course).filter(Course.id == courseid).one_or_none():
            self.write("Failure: Course exists\n")
            return
        newcourse = Course(courseid, user)
        db.add(newcourse)
        db.commit()
        self.write("Success\n")

class TestGetCoursesHandler(RequestHandler):
    def get(self):
        db = Session()
        for c in db.query(Course).all():
            self.write("Found course %s, taught by instructors %s\n" %
                       (c.id, [i.id for i in c.instructors]))

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
             TestGetCoursesHandler),
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + 'createcourse/([^/]+)?',
             TestCreateCourseHandler),
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + 'courses',
             ListCourses),
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
