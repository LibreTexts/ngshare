# nbgrader APIs
# https://github.com/jupyter/nbgrader/issues/659

import os, json, operator

from app import request, app
from helper import (json_success, json_error, error_catcher, db_call,
					json_files_pack, json_files_unpack)

# Initialize database
from database.database import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
db_exists = os.path.exists('/tmp/vserver.db')
engine = create_engine('sqlite:////tmp/vserver.db')
Base.metadata.bind = engine
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

if not db_exists:
	db = Session()
	uk = User('Kevin')
	ua = User('Abigail')
	ul = User('Lawrence')
	ue = User('Eric')
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
	db.add(s1)
	db.add(s2)
	aa.files.append(File('file0', b'00000'))
	ab.files.append(File('file1', b'11111'))
	ac.files.append(File('file2', b'22222'))
	s1.files.append(File('file3', b'33333'))
	s2.files.append(File('file4', b'44444'))
	s1.feedbacks.append(File('file5', b'55555'))
	s2.feedbacks.append(File('file6', b'66666'))
	db.commit()

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

