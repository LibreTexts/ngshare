'''
	nbgrader APIs for vserver
	Similar to https://github.com/jupyter/nbgrader/issues/659
	Authentication
		To make things easy, we are simply putting the user id in HTTP GET
		 parameter or POST data using key `user`.
		For example: /api/courses?user=Eric
'''

import os, json, operator

from app import request
from helper import (json_success, error_catcher, json_files_pack,
					json_files_unpack, strftime, strptime, get_user,
					find_course, find_assignment, find_course_student,
					find_student_submissions, find_student_latest_submission,
					find_student_submission, JsonError, app_get, app_post,
					check_course_student, check_course_instructor,
					check_course_related)
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

@app_get('/api/courses')
def list_courses() :
	'''
		GET /api/courses
		List all available courses the user is taking or teaching (anyone)
	'''
	db = Session()
	user = get_user(db)
	courses = set()
	for i in user.teaching :
		courses.add(i.id)
	for i in user.taking :
		courses.add(i.id)
	return json_success(courses=sorted(courses))

@app_post('/api/course/<course_id>')
def add_course(course_id) :
	'''
		POST /api/course/<course_id>
		Add a course (anyone)
	'''
	db = Session()
	user = get_user(db)
	if db.query(Course).filter(Course.id == course_id).one_or_none() :
		raise JsonError('Course already exists')
	course = Course(course_id, user)
	db.add(course)
	db.commit()
	return json_success()

@app_get('/api/assignments/<course_id>')
def list_assignments(course_id) :
	'''
		GET /api/assignments/<course_id>
		List all assignments for a course (students+instructors)
	'''
	db = Session()
	user = get_user(db)
	course = find_course(db, course_id)
	check_course_related(db, course, user)
	assignments = course.assignments
	return json_success(assignments=list(map(lambda x: x.id, assignments)))

@app_get('/api/assignment/<course_id>/<assignment_id>')
def download_assignment(course_id, assignment_id) :
	'''
		GET /api/assignment/<course_id>/<assignment_id>
		Download a copy of an assignment (students+instructors)
	'''
	db = Session()
	user = get_user(db)
	course = find_course(db, course_id)
	check_course_related(db, course, user)
	assignment = find_assignment(db, course, assignment_id)
	list_only = request.args.get('list_only', 'false') == 'true'
	return json_success(files=json_files_pack(assignment.files, list_only))

@app_post('/api/assignment/<course_id>/<assignment_id>')
def release_assignment(course_id, assignment_id) :
	'''
		POST /api/assignment/<course_id>/<assignment_id>
		Release an assignment (instructors only)
	'''
	db = Session()
	user = get_user(db)
	course = find_course(db, course_id)
	check_course_instructor(db, course, user)
	if db.query(Assignment).filter(Assignment.id == assignment_id,
									Assignment.course == course).one_or_none() :
		raise JsonError('Assignment already exists')
	assignment = Assignment(assignment_id, course)
	json_files_unpack(request.form.get('files'), assignment.files)
	db.commit()
	return json_success()

@app_get('/api/submissions/<course_id>/<assignment_id>')
def list_submissions(course_id, assignment_id) :
	'''
		GET /api/submissions/<course_id>/<assignment_id>
		List all submissions for an assignment from all students
		 (instructors only)
	'''
	db = Session()
	user = get_user(db)
	course = find_course(db, course_id)
	check_course_instructor(db, course, user)
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

@app_get('/api/submissions/<course_id>/<assignment_id>/<student_id>')
def list_student_submission(course_id, assignment_id, student_id) :
	'''
		GET /api/submissions/<course_id>/<assignment_id>/<student_id>
		List all submissions for an assignment from a particular student 
		 (instructors+students, students restricted to their own submissions)
	'''
	db = Session()
	user = get_user(db)
	course = find_course(db, course_id)
	if user.id != student_id :
		check_course_instructor(db, course, user)
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

@app_post('/api/submission/<course_id>/<assignment_id>')
def submit_assignment(course_id, assignment_id) :
	'''
		POST /api/submission/<course_id>/<assignment_id>
		Submit a copy of an assignment (students+instructors)
	'''
	db = Session()
	user = get_user(db)
	course = find_course(db, course_id)
	check_course_related(db, course, user)
	assignment = find_assignment(db, course, assignment_id)
	submission = Submission(user, assignment)
	json_files_unpack(request.form.get('files'), submission.files)
	db.commit()
	return json_success()

@app_get('/api/submission/<course_id>/<assignment_id>/<student_id>')
def download_submission(course_id, assignment_id, student_id) :
	'''
		GET /api/submission/<course_id>/<assignment_id>/<student_id>
		Download a student's submitted assignment (instructors only)
		TODO: maybe allow student to see their own submissions?
	'''
	db = Session()
	user = get_user(db)
	course = find_course(db, course_id)
	check_course_instructor(db, course, user)
	assignment = find_assignment(db, course, assignment_id)
	student = find_course_student(db, course, student_id)
	submission = find_student_latest_submission(db, assignment, student)
	list_only = request.args.get('list_only', 'false') == 'true'
	return json_success(files=json_files_pack(submission.files, list_only),
						timestamp=strftime(submission.timestamp),
						random=submission.random)

@app_post('/api/feedback/<course_id>/<assignment_id>/<student_id>')
def upload_feedback(course_id, assignment_id, student_id) :
	'''
		POST /api/feedback/<course_id>/<assignment_id>/<student_id>
		Upload feedback on a student's assignment (instructors only)
	'''
	db = Session()
	user = get_user(db)
	course = find_course(db, course_id)
	check_course_instructor(db, course, user)
	assignment = find_assignment(db, course, assignment_id)
	student = find_course_student(db, course, student_id)
	if 'timestamp' not in request.form :
		raise JsonError('Please supply timestamp')
	timestamp = strptime(request.form.get('timestamp'))
	if 'random' not in request.form :
		raise JsonError('Please supply random str')
	random_str = request.form.get('random')
	submission = find_student_submission(db, assignment, student, timestamp,
										random_str)
	submission.feedbacks.clear()
	# TODO: does this automatically remove the files?
	json_files_unpack(request.form.get('files'), submission.feedbacks)
	db.commit()
	return json_success()

@app_get('/api/feedback/<course_id>/<assignment_id>/<student_id>')
def download_feedback(course_id, assignment_id, student_id) :
	'''
		GET /api/feedback/<course_id>/<assignment_id>/<student_id>
		Download feedback on a student's assignment
		 (instructors+students, students restricted to their own submissions)
	'''
	db = Session()
	user = get_user(db)
	course = find_course(db, course_id)
	if user.id != student_id :
		check_course_instructor(db, course, user)
	assignment = find_assignment(db, course, assignment_id)
	student = find_course_student(db, course, student_id)
	if 'timestamp' not in request.args :
		raise JsonError('Please supply timestamp')
	timestamp = strptime(request.args.get('timestamp'))
	if 'random' not in request.args :
		raise JsonError('Please supply random str')
	random_str = request.args.get('random')
	submission = find_student_submission(db, assignment, student, timestamp,
										random_str)
	list_only = request.args.get('list_only', 'false') == 'true'
	return json_success(files=json_files_pack(submission.feedbacks, list_only),
						timestamp=strftime(submission.timestamp),
						random=submission.random)

