# Helper functions

import os, json, sqlite3, base64, binascii

from app import request
from settings import FS_PREFIX

from database.database import *

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

def json_files_pack(file_list) :
	'Generate JSON file list (directory tree) from a list of File objects'
	ans = []
	for i in file_list :
		ans.append({
			'path': i.filename, 
			'content': base64.encodebytes(i.contents).decode(),
		})
	return ans

def json_files_unpack(json_obj) :
	'Generate a list of File objects from a JSON file list (directory tree)'
	ans = []
	for i in json_obj :
		try :
			content = base64.decodebytes(i['content'].encode())
		except binascii.Error :
			raise JsonError('Content cannot be base64 decoded')
		ans.append(File(i['path'], content))
	return ans

