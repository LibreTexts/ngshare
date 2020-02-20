# Helper functions

import os, json, sqlite3

from app import request, app
from settings import FS_PREFIX, DB_NAME
from init import db_init

def json_success(msg=None, **kwargs) :
	assert 'message' not in kwargs
	resp = {'success': True, **kwargs}
	if msg is not None :
		resp['message'] = msg
	return json.dumps(resp)

def json_error(msg, **kwargs) :
	assert 'message' not in kwargs
	return json.dumps({'success': False, 'message': msg, **kwargs})

class JsonError(Exception) :
	def __init__(self, msg, **kwargs) :
		self.error = json_error(msg, **kwargs)

def error_catcher(function) :
	def call(*args, **kwargs) :
		try :
			return function(*args, **kwargs)
		except JsonError as e :
			return e.error
	call.__name__ = function.__name__ + '_caller'
	return call

# For unix APIs

def path_modifier(path, escape=lambda x: x) :
	'''
		Modify path so that it possibly will not modify the system
		Note that it does not check for parent directory attack (..)
		escape is a function that escapes a string
	'''
	assert path.startswith('/')
	return os.path.join(escape(FS_PREFIX), path[1:])

def get_pathname(key='pathname', escape=lambda x: x) :
	'Get pathname from HTTP GET, and convert using path_modifier'
	pathname = request.args.get(key)
	if pathname is None :
		raise JsonError('Please supply %s using HTTP GET' % key)
	if not pathname.startswith('/') :
		raise JsonError('%s should be absolute' % key)
	actual_path = path_modifier(pathname)
	return actual_path

def remove_pathname(pathname) :
	assert pathname.startswith(FS_PREFIX)
	return pathname[len(FS_PREFIX.rstrip('/')):]

# For nbgrader APIs

def db_call(cmd, *args) :
	'''
		Execute any database command, ignoring efficiency and security
		But I believe allowing SQL injection is more difficult than not allowing
		e.g. db_call('SELECT ... WHERE id=$1;', '1')
	'''
	if not os.path.exists(DB_NAME) :
		db_init(True)
	conn = sqlite3.connect(DB_NAME)
	result = conn.execute(cmd, args).fetchall()
	conn.commit()
	conn.close()
	return result

def json_files(files_id) :
	'Fetch and generate file list (directory tree) from files_id'
	files = db_call(
			"SELECT file_name, content FROM file_content WHERE files_id=$1",
			files_id
		)
	ans = []
	for file_name, content in files :
		ans.append({"path": file_name, "content": content})
	return ans

