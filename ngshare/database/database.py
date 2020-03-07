'''
    Database structure for NGShare
'''

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=fixme

import datetime
import hashlib

from sqlalchemy import Table, Column, INTEGER, TEXT, BLOB, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Instructor -> Course (Many to Many)
instructor_assoc_table = Table(
    'instructor_assoc_table', Base.metadata,
    Column('left_id', TEXT, ForeignKey('users.id')),
    Column('right_id', INTEGER, ForeignKey('courses._id'))
)

# Student -> Course (Many to Many)
student_assoc_table = Table(
    'student_assoc_table', Base.metadata,
    Column('left_id', TEXT, ForeignKey('users.id')),
    Column('right_id', INTEGER, ForeignKey('courses._id'))
)

# Assignment -> Course (One to Many)
assignment_files_assoc_table = Table(
    'assignment_files_assoc_table', Base.metadata,
    Column('left_id', TEXT, ForeignKey('assignments._id')),
    Column('right_id', INTEGER, ForeignKey('files._id'))
)

# Submission -> Course (One to Many)
submission_files_assoc_table = Table(
    'submission_files_assoc_table', Base.metadata,
    Column('left_id', TEXT, ForeignKey('submissions._id')),
    Column('right_id', INTEGER, ForeignKey('files._id'))
)

# Submission (feedback) -> Course (One to Many)
feedback_files_assoc_table = Table(
    'feedback_files_assoc_table', Base.metadata,
    Column('left_id', TEXT, ForeignKey('submissions._id')),
    Column('right_id', INTEGER, ForeignKey('files._id'))
)

class User(Base):
    'A JupyterHub user; can be either instructor or student, or both'
    __tablename__ = 'users'
    id = Column(TEXT, primary_key=True)
    teaching = relationship("Course", secondary=instructor_assoc_table,
                            back_populates="instructors")
    taking = relationship("Course", secondary=student_assoc_table,
                          back_populates="students")

    def __init__(self, name):
        self.id = name

    def __str__(self):
        return '<User %s>' % self.id

    @staticmethod
    def from_jupyterhub_user(user_model, db):
        'Import users from JupyterHub'
        user_name = user_model['name']
        user = db.query(User).filter(User.id == user_name).one_or_none()
        if user is None:
            user = User(user_name)
            db.add(user)
            db.commit()
        return user

class Course(Base):
    'An nbgrader course'
    __tablename__ = 'courses'
    # in case course name needs to be changed
    _id = Column(INTEGER, primary_key=True)
    id = Column(TEXT, unique=True)
    instructors = relationship("User", secondary=instructor_assoc_table,
                               back_populates="teaching")
    students = relationship("User", secondary=student_assoc_table,
                            back_populates="taking")
    assignments = relationship("Assignment", backref="course")

    def __init__(self, name, instructor):
        self.id = name
        self.instructors.append(instructor)

    def __str__(self):
        return '<Course %s>' % self.id

class Assignment(Base):
    'An nbgrader assignment'
    __tablename__ = 'assignments'
    # in case assignment name needs to be changed
    _id = Column(INTEGER, primary_key=True)
    id = Column(TEXT)
    course_id = Column(INTEGER, ForeignKey("courses._id"))
    submissions = relationship("Submission", backref="assignment")
    files = relationship("File", secondary=assignment_files_assoc_table)
    released = BOOLEAN()
    due = Column(TIMESTAMP)
    # TODO: timezoon

    def __init__(self, name, course):
        self.id = name
        self.course = course

    def __str__(self):
        return '<Assignment %s>' % self.id

class Submission(Base):
    'A submission for an assignment'
    __tablename__ = 'submissions'
    _id = Column(INTEGER, primary_key=True)
    assignment_id = Column(INTEGER, ForeignKey("assignments._id"))
    timestamp = Column(TIMESTAMP)
    student_id = Column(TEXT, ForeignKey("users.id"))
    files = relationship("File", secondary=submission_files_assoc_table)
    feedbacks = relationship("File", secondary=feedback_files_assoc_table)
    student = relationship("User")

    def __init__(self, student, assignment):
        self.timestamp = datetime.datetime.now()
        self.student = student
        self.assignment = assignment

    def __str__(self):
        return '<Submission %d>' % self._id

class File(Base):
    'A File (for assignment, submission file, or submission feedback)'
    __tablename__ = 'files'
    _id = Column(INTEGER, primary_key=True)
    filename = Column(TEXT)
    contents = Column(BLOB)
    checksum = Column(TEXT)

    def __init__(self, filename, contents):
        self.filename = filename
        self.contents = contents
        self.checksum = hashlib.md5(contents).hexdigest()

    def __str__(self):
        return '<File %s>' % self.filename
