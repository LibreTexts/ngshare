import sys
import json
import simplejson
import base64
import requests

URL_PREFIX = 'http://127.0.0.1:11111'
GET = requests.get
POST = requests.post

def request_page(url, params={}, method=GET) :
	assert url.startswith('/') and not url.startswith('//')
	resp = method(URL_PREFIX + url, params=params)
	return resp.json()

def assert_success(url, params={}, method=GET) :
	resp = request_page(url, params, method)
	if resp['success'] != True :
		print(repr(resp), file=sys.stderr)
		raise Exception('Not success')
	return resp

def assert_fail(url, params={}, method=GET) :
	resp = request_page(url, params, method)
	if resp['success'] != False :
		print(repr(resp), file=sys.stderr)
		raise Exception('Success')
	return resp

# Run init.py before running the test

def test_init() :
	import os, time
	from settings import DB_NAME
	assert DB_NAME.startswith('sqlite:///')
	os.unlink(DB_NAME[len('sqlite:///'):])
	os.system('touch vserver.py')
	time.sleep(2)

def test_list_assignments() :
	assert assert_success('/api/assignments/course2')['assignments'] == \
			['assignment2a', 'assignment2b']
	assert assert_fail('/api/assignments/jkl')['message'] == \
			'Course not found'

def test_download_assignment() :
	files = assert_success('/api/assignment/course1/challenge')['files']
	assert files[0]['path'] == 'file2'
	assert base64.b64decode(files[0]['content'].encode()) == b'22222'
	assert assert_fail('/api/assignment/jkl/challenger')['message'] == \
			'Course not found'
	assert assert_fail('/api/assignment/course1/challenger')['message'] == \
			'Assignment not found'

def test_release_assignment() :
	params = {'files': json.dumps([{'path': 'a', 'content': 'amtsCg=='},
									{'path': 'b', 'content': 'amtsCg=='}])}
	assert assert_fail('/api/assignment/jkl/challenger', method=POST, 
						params=params)['message'] == 'Course not found'
	assert_success('/api/assignment/course1/challenger', method=POST, 
					params=params)
	assert assert_fail('/api/assignment/course1/challenger', method=POST, 
						params=params)['message'] == 'Assignment already exists'

def test_list_submissions() :
	assert assert_fail('/api/submissions/jkl/challenge')['message'] == \
			'Course not found'
	assert assert_fail('/api/submissions/course1/challenges')['message'] == \
			'Assignment not found'
	result = assert_success('/api/submissions/course1/challenge')
	assert len(result['submissions']) == 2
	assert result['submissions'][0]['student_id'] == 'Lawrence'
	assert result['submissions'][1]['student_id'] == 'Lawrence'
	result = assert_success('/api/submissions/course2/assignment2a')
	assert len(result['submissions']) == 0

def test_list_student_submission() :
	assert assert_fail('/api/submissions/jkl/challenge/st')['message'] == \
			'Course not found'
	assert assert_fail('/api/submissions/course1/challenges/st')['message'] == \
			'Assignment not found'
	assert assert_fail('/api/submissions/course1/challenge/st')['message'] == \
			'Student not found'
	result = assert_success('/api/submissions/course1/challenge/Lawrence')
	assert len(result['submissions']) == 2
	result = assert_success('/api/submissions/course2/assignment2a/Eric')
	assert len(result['submissions']) == 0
