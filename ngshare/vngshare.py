'''
    vngshare - Vserver-like Notebook Grader Share
    Similar to vserver; allows easy testing.
'''

# pylint: disable=abstract-method
# pylint: disable=function-redefined
# pylint: disable=invalid-name
# pylint: disable=no-member
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import

import sys
from ngshare import *
from database.test_database import clear_db, init_db

class MockAuth(HubAuthenticated):
    '''
        Mock class substituting HubAuthenticated
    '''
    def get_login_url(self):
        return 'http://example.com/'

    def get_current_user(self):
        if type(self).__name__ in ('HomePage', 'Favicon', 'InitDatabase'):
            user = self.get_argument('user', 'user')
        else:
            user = self.get_argument('user')
        return {'name': user}

MyRequestHandler.__bases__ = (MockAuth, RequestHandler, MyHelpers)

class InitDatabase(MyRequestHandler):
    '/initialize-Data6ase'
    @authenticated
    def get(self):
        'Initialize database similar to in vserver'
        # Dangerous: do not use in production
        clear_db(self.db)
        init_db(self.db)
        self.json_success('done')

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

    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 12121

    http_server = HTTPServer(app)
    http_server.listen(port, host)

    print('Starting vngshare (Vserver-like Notebook Grader Share)')
    print('Database file is /tmp/ngshare.db')
    print('Please go to http://%s:%d/api/' % (host, port))
    IOLoop.current().start()

if __name__ == '__main__':
    main()
