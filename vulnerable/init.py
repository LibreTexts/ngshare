import sqlite3
import datetime

from database.database import *

def init_test_data(Session) :
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
	s1.timestamp = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
	s1.random = '12345678-90ab-cdef-0123-456789abcdef'
	db.add(s1)
	db.add(s2)
	aa.files.append(File('file0', b'00000'))
	ab.files.append(File('file1', b'11111'))
	ac.files.append(File('file2', b'22222'))
	s1.files.append(File('file3', b'33333'))
	s2.files.append(File('file4', b'44444'))
	s1.feedbacks.append(File('file5', b'55555'))
	db.commit()

