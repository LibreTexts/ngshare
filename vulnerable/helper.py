# Helper functions

import os, json, sqlite3, base64, binascii, datetime

from app import app, request
from settings import FS_PREFIX

from database.database import *

def json_success(msg=None, **kwargs) :
	assert 'success' not in kwargs and 'message' not in kwargs
	resp = {'success': True, **kwargs}
	if msg is not None :
		resp['message'] = msg
	return json.dumps(resp)

def json_error(msg, **kwargs) :
	assert 'success' not in kwargs and 'message' not in kwargs
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

def app_get(url) :
	return lambda func: app.route(url)(error_catcher(func))

def app_post(url) :
	return lambda func: app.route(url, methods=["POST"])(error_catcher(func))

def strftime(dt) :
	'Use API specified format to strftime'
	# TODO: follow API specification
	return dt.strftime('%Y-%m-%d %H:%M:%S.%f %Z')

def strptime(string) :
	'Use API specified format to strptime'
	try :
		return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f %Z')
	except ValueError :
		try :
			return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f ')
		except ValueError :
			raise JsonError('Time format incorrect')

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

def path_check(pathname) :
	'''
		Return whether a pathname (for file, in director tree) is safe
		Current policy:
			Not empty
			os.path.abspath resolves to a child address
			Path does not contain ('.', '..', '', '/')
		Note: os.path.abspath is used instead of os.path.realpath to prevent
		 symbolic link issues, because the file is not on server
		Note: os.path.abspath is not 100% safe
		Note: currently only using Linux pathname conventions
	'''
	if not pathname :
		return False
	path = pathname
	while path :
		path, name = os.path.split(path)
		if name in ('.', '..', '', '/') :
			return False
	working = os.path.abspath('.')
	target = os.path.abspath(pathname)
	if os.path.commonpath([working, target]) != working :
		return False
	return True

def get_user(db) :
	# TODO: user nbgrader API
	username = request.args.get('user')
	if username is None :
		username = request.form.get('user')
		if username is None :
			raise JsonError('Login required (Please supply user)')
	user = db.query(User).filter(User.id == username).one_or_none()
	if user is None :
		raise JsonError('Login required (User not found)')
	return user

def json_files_pack(file_list, list_only) :
	'Generate JSON file list (directory tree) from a list of File objects'
	ans = []
	for i in file_list :
		if list_only :
			ans.append({
				'path': i.filename,
			})
		else :
			ans.append({
				'path': i.filename,
				'content': base64.encodebytes(i.contents).decode(),
			})
	return ans

def json_files_unpack(json_str, target) :
	'''
		Generate a list of File objects from a JSON file list (directory tree)
		json_str: json object as string; raise error when None
		target: a list to put file objects in
	'''
	if json_str is None :
		raise JsonError('Please supply files')
	try :
		json_obj = json.loads(json_str)
	except json.decoder.JSONDecodeError :
		raise JsonError('Files cannot be JSON decoded')
	for i in json_obj :
		if not path_check(i['path']) :
			raise JsonError('Illegal path')
		try :
			content = base64.decodebytes(i['content'].encode())
		except binascii.Error :
			raise JsonError('Content cannot be base64 decoded')
		target.append(File(i['path'], content))

def find_course(db, course_id) :
	'Return a Course object from id, or raise error'
	course = db.query(Course).filter(Course.id == course_id).one_or_none()
	if course is None :
		raise JsonError('Course not found')
	return course

def find_assignment(db, course, assignment_id) :
	'Return an Assignment object from course and id, or raise error'
	assignment = db.query(Assignment).filter(
		Assignment.id == assignment_id,
		Assignment.course == course).one_or_none()
	if assignment is None :
		raise JsonError('Assignment not found')
	return assignment

def find_course_student(db, course, student_id) :	
	'Return a Student object from course and id, or raise error'
	student = db.query(User).filter(
		User.id == student_id, 
		User.taking.contains(course)).one_or_none()
	if student is None :
		raise JsonError('Student not found')
	return student

def find_student_submissions(db, assignment, student) :
	'Return a list of Submission objects from assignment and student'
	return db.query(Submission).filter(
		Submission.assignment == assignment,
		Submission.student == student.id)

def find_student_latest_submission(db, assignment, student) :
	'Return the latest Submission object from assignment and studnet, or error'
	submission = find_student_submissions(db, assignment, student).order_by(
				Submission.timestamp.desc()).first()
	if submission is None :
		raise JsonError('Submission not found')
	return submission

def find_student_submission(db, assignment, student, timestamp, random_str) :
	'Return the Submission object from timestamp etc, or error'
	submission = find_student_submissions(db, assignment, student).filter(
				Submission.timestamp==timestamp,
				Submission.random==random_str).one_or_none()
	if submission is None :
		raise JsonError('Submission not found')
	return submission

# Auth APIs

def is_course_student(db, course, user) :
	'Return whether user is a student in the course'
	return course in user.taking

def is_course_instructor(db, course, user) :
	'Return whether user is an instructor in the course'
	return course in user.teaching

def check_course_student(db, course, user) :
	'Assert user is a student in the course'
	if not is_course_student(db, course, user) :
		raise JsonError('Permission denied (not course student)')

def check_course_instructor(db, course, user) :
	'Assert user is an instructor in the course'
	if not is_course_instructor(db, course, user) :
		raise JsonError('Permission denied (not course instructor)')

def check_course_related(db, course, user) :
	'Assert user is a student or an instructor in the course'
	if not is_course_instructor(db, course, user) and \
		not is_course_student(db, course, user) :
		raise JsonError('Permission denied (not related to course)')
