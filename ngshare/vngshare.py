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
    parser = argparse.ArgumentParser(
        description='vngshare, Vserver-like ngshare (Notebook Grader Share)')
    parser.add_argument('--prefix', help='URL prefix', default='/api/')
    parser.add_argument('--debug', help='Output debug information')
    parser.add_argument('--database', help='Database url',
                        default='sqlite:////tmp/ngshare.db')
    parser.add_argument('--host', help='Bind hostname', default='127.0.0.1')
    parser.add_argument('--port', help='Bind hostname', type=int, default=12121)
    args = parser.parse_args()

    prefix = args.prefix
    extra_handlers = [(prefix + 'initialize-Data6ase', InitDatabase)]
    app = MyApplication(prefix, args.database, extra_handlers, debug=True)

    http_server = HTTPServer(app)
    http_server.listen(args.port, args.host)

    print('Starting vngshare (Vserver-like Notebook Grader Share)')
    print('Database file is %s' % repr(args.database))
    print('Please go to http://%s:%d/api/' % (args.host, args.port))
    IOLoop.current().start()

if __name__ == '__main__':
    main()
