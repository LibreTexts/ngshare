# nbgrader APIs
# https://github.com/jupyter/nbgrader/issues/659

import os, json, operator

from app import request, app
from helper import (json_success, json_error, error_catcher, json_files_pack,
					json_files_unpack, strftime, find_course, find_assignment,
					find_course_student, find_student_submissions)
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

@app.route('/api/courses')
@error_catcher
def list_courses() :
	'''
		GET /api/courses
		List all courses
	'''
	db = Session()
	# TODO: limit to courses user is taking
	courses = []
	for i in db.query(Course).filter().all() :
		courses.append(i.id)
	return json_success(courses=courses)

@app.route('/api/assignments/<course_id>')
@error_catcher
def list_assignments(course_id) :
	'''
		GET /api/assignments/<course_id>
		List all assignments for a course (students+instructors)
	'''
	db = Session()
	course = find_course(db, course_id)
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
	course = find_course(db, course_id)
	assignment = find_assignment(db, course, assignment_id)
	return json_success(files=json_files_pack(assignment.files))

@app.route('/api/assignment/<course_id>/<assignment_id>', methods=["POST"])
@error_catcher
def release_assignment(course_id, assignment_id) :
	'''
		POST /api/assignment/<course_id>/<assignment_id>
		Release an assignment (instructors only)
	'''
	db = Session()
	course = find_course(db, course_id)
	if db.query(Assignment).filter(Assignment.id == assignment_id,
									Assignment.course == course).one_or_none() :
		return json_error('Assignment already exists')
	assignment = Assignment(assignment_id, course)
	json_files_unpack(request.form.get('files'), assignment.files)
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
	db = Session()
	course = find_course(db, course_id)
	assignment = find_assignment(db, course, assignment_id)
	submissions = []
	for submission in assignment.submissions :
		submissions.append({
			'student_id': submission.student, 
			'timestamp': strftime(submission.timestamp), 
			'random': submission.random, 
			# TODO: "notebooks": [], 
		})
	return json_success(submissions=submissions)

@app.route('/api/submissions/<course_id>/<assignment_id>/<student_id>')
@error_catcher
def list_student_submission(course_id, assignment_id, student_id) :
	'''
		GET /api/submissions/<course_id>/<assignment_id>/<student_id>
		List all submissions for an assignment from a particular student 
		 (instructors+students, students restricted to their own submissions)
	'''
	db = Session()
	course = find_course(db, course_id)
	assignment = find_assignment(db, course, assignment_id)
	student = find_course_student(db, course, student_id)
	submissions = []
	for submission in find_student_submissions(db, assignment, student) :
		submissions.append({
			'student_id': submission.student, 
			'timestamp': strftime(submission.timestamp), 
			'random': submission.random, 
			# TODO: "notebooks": [], 
		})
	return json_success(submissions=submissions)

@app.route('/api/submission/<course_id>/<assignment_id>/<student_id>', 
			methods=["POST"])
@error_catcher
def submit_assignment(course_id, assignment_id, student_id) :
	'''
		POST /api/submission/<course_id>/<assignment_id>/<student_id>
		Submit a copy of an assignment (students+instructors)
	'''
	db = Session()
	course = find_course(db, course_id)
	assignment = find_assignment(db, course, assignment_id)
	student = find_course_student(db, course, student_id)
	submission = Submission(student, assignment)
	json_files_unpack(request.form.get('files'), submission.files)
	db.commit()
	return json_success()

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
