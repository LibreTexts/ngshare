# nbgrader APIs
# https://github.com/jupyter/nbgrader/issues/659

import os, json, operator

from app import request, app
from helper import (json_success, json_error, error_catcher,
					json_files_pack, json_files_unpack)
from settings import DB_NAME
from init import init_test_data

# Initialize database
from database.database import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
db_exists = os.path.exists('/tmp/vserver.db')
engine = create_engine(DB_NAME)
Base.metadata.bind = engine
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

if not db_exists:
	init_test_data(Session)

@app.route('/api/assignments/<course_id>')
@error_catcher
def list_assignments(course_id) :
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
	db = Session()
	course = db.query(Course).filter(Course.id == course_id).one_or_none()
	if course is None :
		return json_error('Course not found')
	assignments = course.assignments
	return json_success(assignments=list(map(lambda x: x.id, assignments)))

@app.route('/api/assignment/<course_id>/<assignment_id>')
@error_catcher
def download_assignment(course_id, assignment_id) :
	'''
		GET /api/assignment/<course_id>/<assignment_id>
		Download a copy of an assignment (students+instructors)
	'''
	db = Session()
	course = db.query(Course).filter(Course.id == course_id).one_or_none()
	if course is None :
		return json_error('Course not found')
	assignment = db.query(Assignment).filter(
		Assignment.id == assignment_id,
		Assignment.course == course).one_or_none()
	if assignment is None :
		return json_error('Assignment not found')
	return json_success(files=json_files_pack(assignment.files))

@app.route('/api/assignment/<course_id>/<assignment_id>', methods=["POST"])
@error_catcher
def release_assignment(course_id, assignment_id) :
	'''
		POST /api/assignment/<course_id>/<assignment_id>
		Release an assignment (instructors only)
	'''
	db = Session()
	course = db.query(Course).filter(Course.id == course_id).one_or_none()
	if course is None :
		return json_error('Course not found')
	if db.query(Assignment).filter(Assignment.id == assignment_id,
									Assignment.course == course).one_or_none() :
		return json_error('Assignment already exists')
	assignment = Assignment(assignment_id, course)
	files = request.args.get('files')
	if not files :
		return json_error('Please supply files')
	for i in json_files_unpack(json.loads(files)) :
		assignment.files.append(i)
	db.commit()
	return json_success()

@app.route('/api/submissions/<course_id>/<assignment_id>')
@error_catcher
def list_submissions(course_id, assignment_id) :
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

