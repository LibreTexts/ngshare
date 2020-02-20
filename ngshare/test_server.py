"""An example service authenticating with the Hub.
This serves `/services/whoami/`, authenticated with the Hub, showing the user their own info.
"""
from database.database import *
import json
import os
from urllib.parse import urlparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import authenticated
from tornado.web import RequestHandler

from jupyterhub.services.auth import HubAuthenticated

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite://')
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

def main():
    app = Application(
        [
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'], TestGetCoursesHandler),
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + 'createcourse/([^/]+)?', TestCreateCourseHandler),
        ]
    )

    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    http_server.listen(url.port, url.hostname)

    IOLoop.current().start()


if __name__ == '__main__':
    main()
