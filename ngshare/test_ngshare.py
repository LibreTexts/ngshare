from ngshare import *

class MockAuth(HubAuthenticated):
    def get_login_url(self):
        return 'http://example.com/'

    def get_current_user(self):
        user = self.get_argument('user')
        return {'name': user}

MyRequestHandler.__bases__ = (MockAuth, RequestHandler, MyHelpers)

def main():
    'Main function'
    prefix = '/api/'
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
            (prefix + 'initialize-Data6ase', InitDatabase),
            (r'.*', Test404Handler),
        ],
        autoreload=True
    )

    engine = create_engine('sqlite:////tmp/ngshare.db')
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    app.db_session = sessionmaker(bind=engine)

    http_server = HTTPServer(app)
    http_server.listen('12121', '127.0.0.1')

    IOLoop.current().start()

if __name__ == '__main__':
    main()
