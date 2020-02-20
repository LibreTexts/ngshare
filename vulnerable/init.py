import sqlite3

from settings import DB_NAME

def db_init(create_data=False) :
	cmd_list = [
		'''
			PRAGMA foreign_keys=1;
		''', 
		'''
			CREATE TABLE instructors (
				id TEXT PRIMARY KEY
			);
		''', 
		'''
			CREATE TABLE students (
				id TEXT PRIMARY KEY
			);
		''', 
		'''
			CREATE TABLE courses (
				id TEXT PRIMARY KEY,
				instructor_id TEXT,
				FOREIGN KEY (instructor_id) REFERENCES instructors(id)
			);
		''', 
		'''
			CREATE TABLE assignments (
				id TEXT NOT NULL,
				course_id TEXT,
				files_id TEXT,
				PRIMARY KEY (course_id, id),
				FOREIGN KEY (course_id) REFERENCES courses(id)
			);
		''', 
		'''	-- Pointer to a list files
			-- Used by assignment, submission, and feedback
			CREATE TABLE files (
				id TEXT PRIMARY KEY
			);
		''', 
		'''	-- Store actual file list and their content
			-- content is stored in base64 format here
			CREATE TABLE file_content (
				files_id TEXT,
				file_name TEXT,
				content TEXT,
				PRIMARY KEY (files_id, file_name),
				FOREIGN KEY (files_id) REFERENCES files(id)
			);
		''', 
		'''
			CREATE TABLE submissions (
				course_id TEXT,
				assignment_id TEXT,
				student_id TEXT,
				timestamp TEXT,
				files_id TEXT,
				feedback_files_id TEXT,
				PRIMARY KEY (course_id, assignment_id, student_id, timestamp),
				FOREIGN KEY (course_id, assignment_id)
				                         REFERENCES assignments(course_id, id),
				FOREIGN KEY (student_id) REFERENCES students(id),
				FOREIGN KEY (files_id) REFERENCES files(id),
				FOREIGN KEY (feedback_files_id) REFERENCES files(id)
			);
		''', 
		# TODO: how to make sure that the following 3 columns are unique?
		#	assignments.files_id
		#	submissions.files_id
		#	submissions.feedback_files_id
	]
	if create_data :
		cmd_list += [
			"INSERT INTO instructors VALUES ('Kevin');", 
			"INSERT INTO instructors VALUES ('Abigail');", 
			"INSERT INTO students VALUES ('Lawrence');", 
			"INSERT INTO students VALUES ('Eric');", 
			"INSERT INTO courses VALUES ('course1', 'Kevin');", 
			"INSERT INTO courses VALUES ('course2', 'Abigail');", 
			"INSERT INTO files VALUES ('files0')", 
			"INSERT INTO files VALUES ('files1')", 
			"INSERT INTO files VALUES ('files2')", 
			"INSERT INTO files VALUES ('files3')", 
			"INSERT INTO files VALUES ('files4')", 
			"INSERT INTO files VALUES ('files5')", 
			"INSERT INTO files VALUES ('files6')", 
			"INSERT INTO file_content VALUES ('files0', 'file0', '00000')", 
			"INSERT INTO file_content VALUES ('files1', 'file1', '11111')", 
			"INSERT INTO file_content VALUES ('files2', 'file2', '22222')", 
			"INSERT INTO file_content VALUES ('files3', 'file3', '33333')", 
			"INSERT INTO file_content VALUES ('files4', 'file4', '44444')", 
			"INSERT INTO file_content VALUES ('files5', 'file5', '55555')", 
			"INSERT INTO file_content VALUES ('files6', 'file6', '66666')", 
			"INSERT INTO assignments VALUES \
			 ('challenge', 'course1', 'files0');", 
			"INSERT INTO assignments VALUES \
			 ('assignment2a', 'course2', 'files1');", 
			"INSERT INTO assignments VALUES \
			 ('assignment2b', 'course2', 'files2');", 
			"INSERT INTO submissions VALUES \
			 ('course1', 'challenge', 'Lawrence', '2019-20-20', 'files3',null)",
			"INSERT INTO submissions VALUES \
			 ('course1', 'challenge', 'Eric', '2020-20-20', 'files4', null)", 
		]
	conn = sqlite3.connect(DB_NAME)
	for i in cmd_list :
		conn.execute(i)
	conn.commit()
	conn.close()

