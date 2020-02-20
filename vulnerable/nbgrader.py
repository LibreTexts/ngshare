# nbgrader APIs
# https://github.com/jupyter/nbgrader/issues/659

import base64, binascii, operator

from app import request, app
from helper import json_success, json_error, error_catcher, db_call, json_files

@app.route('/api/assignments/<course_id>')
@error_catcher
def assignments_list(course_id) :
	'''
		GET /api/assignments/<course_id>
		List all assignments for a course (students+instructors)
		Response when success
			{
				"success": true, 
				"assignments": [
					'assignment1',
					'assignment2',
					'assignment3'
				]
			}
		Response when course not found
			{
				"success": false, 
				"message": "Course not found"
			}
	'''
	if not db_call('SELECT * FROM courses WHERE id=$1', course_id) :
		return json_error('Course not found')
	table = db_call('SELECT id FROM assignments WHERE course_id=$1;', course_id)
	return json_success(assignments=list(map(operator.itemgetter(0), table)))

@app.route('/api/assignment/<course_id>/<assignment_id>')
@error_catcher
def download_assignment(course_id, assignment_id) :
	'''
		GET /api/assignment/<course_id>/<assignment_id>
		Download a copy of an assignment (students+instructors)
	'''
	if not db_call('SELECT * FROM courses WHERE id=$1', course_id) :
		return json_error('Course not found')
	assignments = db_call(
			'SELECT files_id FROM assignments WHERE course_id=$1 and id=$2',
			course_id, assignment_id
		)
	if not assignments :
		return json_error('Assignment not found')
	files_id = assignments[0][0]
	return json_success(files=json_files(files_id))

@app.route('/api/assignment/<course_id>/<assignment_id>', methods=["POST"])
@error_catcher
def release_assignment(course_id, assignment_id) :
	'''
		POST /api/assignment/<course_id>/<assignment_id>
		Release an assignment (instructors only)
	'''
	raise NotImplementedError

@app.route('/api/submissions/<course_id>/<assignment_id>')
@error_catcher
def list_assignments(course_id, assignment_id) :
	'''
		GET /api/submissions/<course_id>/<assignment_id>
		List all submissions for an assignment from all students
		 (instructors only)
	'''
	raise NotImplementedError

@app.route('/api/submissions/<course_id>/<assignment_id>/<student_id>')
@error_catcher
def list_student_submission(course_id, assignment_id, student_id) :
	'''
		GET /api/submissions/<course_id>/<assignment_id>/<student_id>
		List all submissions for an assignment from a particular student 
		 (instructors+students, students restricted to their own submissions)
	'''
	raise NotImplementedError

@app.route('/api/submission/<course_id>/<assignment_id>/<student_id>', 
			methods=["POST"])
@error_catcher
def submit_assignment(course_id, assignment_id, student_id) :
	'''
		POST /api/submission/<course_id>/<assignment_id>/<student_id>
		Submit a copy of an assignment (students+instructors)
	'''
	raise NotImplementedError

@app.route('/api/submission/<course_id>/<assignment_id>/<student_id>')
@error_catcher
def download_submission(course_id, assignment_id, student_id) :
	'''
		GET /api/submission/<course_id>/<assignment_id>/<student_id>
		Download a student's submitted assignment (instructors only)
		TODO: maybe allow student to see their own submissions?
	'''
	raise NotImplementedError

@app.route('/api/feedback/<course_id>/<assignment_id>/<student_id>', 
			methods=["POST"])
@error_catcher
def upload_feedback(course_id, assignment_id, student_id) :
	'''
		POST /api/feedback/<course_id>/<assignment_id>/<student_id>
		Upload feedback on a student's assignment (instructors only)
	'''
	raise NotImplementedError

@app.route('/api/feedback/<course_id>/<assignment_id>/<student_id>')
@error_catcher
def download_feedback(course_id, assignment_id, student_id) :
	'''
		GET /api/feedback/<course_id>/<assignment_id>/<student_id>
		Download feedback on a student's assignment
		 (instructors+students, students restricted to their own submissions)
	'''
	raise NotImplementedError

