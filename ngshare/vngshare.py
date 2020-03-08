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

def main():
    'Main function'
    prefix = '/api/'
    app = Application(
        [
            (prefix, HomePage),
            (prefix + 'favicon.ico', Favicon),
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
