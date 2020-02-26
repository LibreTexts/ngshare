from database.database import *
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

class TestCreateCourseHandler(HubAuthenticated, RequestHandler):
    @authenticated
    def post(self, courseid):
        user_model = self.get_current_user()
        db = Session()
        user = db.query(User).filter(User.id == user_model['name']).one_or_none()
        if not user:
            user = User(user_model['name'])
            db.add(user)
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
            self.write("Found course %s, taught by instructors %s\n"%(c.id, [i.id for i in c.instructors]))

class Test404Handler(RequestHandler):
    def get(self):
        self.write("This would have 404'd. Double check URL.\n")
        self.write(json.dumps(dict(os.environ), indent=1, sort_keys=True))
        self.write("\n"+self.request.uri+"\n"+self.request.path+"\n")

def main():

    parser = argparse.ArgumentParser(description='ngshare, a REST API nbgrader exchange')
    parser.add_argument('--jupyterhub_api_url', help='Override the JUPYTERHUB_API_URL environment variable')
    args=parser.parse_args()
    if args.jupyterhub_api_url is not None:
        os.environ['JUPYTERHUB_API_URL']=args.jupyterhub_api_url

    app = Application(
        [
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'], TestGetCoursesHandler),
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + 'createcourse/([^/]+)?', TestCreateCourseHandler),
            (r'.*', Test404Handler),
        ]
    )

    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    http_server.listen(url.port, '0.0.0.0') #must listen on all interfaces for proxy

    IOLoop.current().start()


if __name__ == '__main__':
    main()
