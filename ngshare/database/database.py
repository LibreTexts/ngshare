'''
    Database structure for NGShare
'''

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=fixme

import datetime
import hashlib

from sqlalchemy import (Table, Column, INTEGER, TEXT, BLOB, TIMESTAMP, BOOLEAN,
                        ForeignKey)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Student -> Course (Many to Many)
student_assoc_table = Table(
    'student_assoc_table', Base.metadata,
    Column('left_id', TEXT, ForeignKey('users.id'), primary_key=True),
    Column('right_id', INTEGER, ForeignKey('courses._id'), primary_key=True),
)

# Assignment -> Course (One to Many)
assignment_files_assoc_table = Table(
    'assignment_files_assoc_table', Base.metadata,
    Column('left_id', TEXT, ForeignKey('assignments._id'), primary_key=True),
    Column('right_id', INTEGER, ForeignKey('files._id'), primary_key=True),
)

# Submission -> Course (One to Many)
submission_files_assoc_table = Table(
    'submission_files_assoc_table', Base.metadata,
    Column('left_id', TEXT, ForeignKey('submissions._id'), primary_key=True),
    Column('right_id', INTEGER, ForeignKey('files._id'), primary_key=True),
)

# Submission (feedback) -> Course (One to Many)
feedback_files_assoc_table = Table(
    'feedback_files_assoc_table', Base.metadata,
    Column('left_id', TEXT, ForeignKey('submissions._id'), primary_key=True),
    Column('right_id', INTEGER, ForeignKey('files._id'), primary_key=True),
)

class User(Base):
    'A JupyterHub user; can be either instructor or student, or both'
    __tablename__ = 'users'
    id = Column(TEXT, primary_key=True)
    teaching = association_proxy('inst_assoc', 'course',
                                    creator=lambda course: InstructorAssociation(
                                        course=a,
                                        first_name='0/0',
                                        last_name='0/0',
                                        email='0/0',
                                    ),
                                    cascade_scalar_deletes=True)
    taking = relationship('Course', secondary=student_assoc_table,
                          back_populates='students')

    def __init__(self, name):
        'Initialize with JupyterHub user name'
        self.id = name

    def __str__(self):
        return '<User %s>' % self.id

    def delete(self, db):
        'Remove user and dependent data'
        raise NotImplementedError('Currently users cannot be deleted')

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
    instructors = association_proxy('inst_assoc', 'user',
                                    creator=lambda user: InstructorAssociation(
                                        user=user,
                                        first_name='0/0',
                                        last_name='0/0',
                                        email='0/0',
                                    ),
                                    cascade_scalar_deletes=True)
    students = relationship('User', secondary=student_assoc_table,
                            back_populates='taking')
    assignments = relationship('Assignment', backref='course')

    def __init__(self, name, instructor):
        'Initialize with course name and teacher'
        self.id = name
        self.instructors.append(instructor)

    def __str__(self):
        return '<Course %s>' % self.id

    def delete(self, db):
        'Remove course and dependent data'
        raise NotImplementedError('Currently courses cannot be deleted')

class Assignment(Base):
    'An nbgrader assignment'
    __tablename__ = 'assignments'
    # in case assignment name needs to be changed
    _id = Column(INTEGER, primary_key=True)
    id = Column(TEXT)
    course_id = Column(INTEGER, ForeignKey('courses._id'))
    submissions = relationship('Submission', backref='assignment')
    files = relationship('File', secondary=assignment_files_assoc_table)
    released = BOOLEAN()
    due = Column(TIMESTAMP)
    # TODO: timezoon

    def __init__(self, name, course):
        'Initialize with assignment name and course'
        self.id = name
        self.course = course

    def __str__(self):
        return '<Assignment %s>' % self.id

    def delete(self, db):
        'Remove assignment and dependent data (files, submissions)'
        for file_obj in self.files:
            file_obj.delete(db)
        for submission in self.submissions:
            submission.delete(db)
        db.delete(self)

class Submission(Base):
    'A submission for an assignment'
    __tablename__ = 'submissions'
    _id = Column(INTEGER, primary_key=True)
    assignment_id = Column(INTEGER, ForeignKey('assignments._id'))
    timestamp = Column(TIMESTAMP)
    student_id = Column(TEXT, ForeignKey('users.id'))
    files = relationship('File', secondary=submission_files_assoc_table)
    feedbacks = relationship('File', secondary=feedback_files_assoc_table)
    student = relationship('User')

    def __init__(self, student, assignment):
        'Initialize with student and assignment'
        self.timestamp = datetime.datetime.now()
        self.student = student
        self.assignment = assignment

    def __str__(self):
        return '<Submission %d>' % self._id

    def delete(self, db):
        'Remove submission and dependent data (files, feedbacks)'
        for file_obj in self.files:
            file_obj.delete(db)
        for file_obj in self.feedbacks:
            file_obj.delete(db)
        db.delete(self)

class File(Base):
    'A File (for assignment, submission file, or submission feedback)'
    __tablename__ = 'files'
    _id = Column(INTEGER, primary_key=True)
    filename = Column(TEXT)
    contents = Column(BLOB)
    checksum = Column(TEXT)

    def __init__(self, filename, contents):
        'Initialize with file name and content; auto-compute md5'
        self.filename = filename
        self.contents = contents
        self.checksum = hashlib.md5(contents).hexdigest()

    def __str__(self):
        return '<File %s>' % self.filename

    def delete(self, db):
        'Remove file'
        db.delete(self)

# Ref: https://stackoverflow.com/a/7524753
# Ref: https://stackoverflow.com/a/23734727
# Instructor -> Course (Many to Many)
class InstructorAssociation(Base):
    'Relationship between instructor and course, with extra data'
    __tablename__ = 'instructor_assoc_table'
    left_id = Column(TEXT, ForeignKey('users.id'), primary_key=True)
    right_id = Column(TEXT, ForeignKey('courses.id'), primary_key=True)
    first_name = Column(TEXT)
    last_name = Column(TEXT)
    email = Column(TEXT)
    user = relationship(User, backref=backref(
        'inst_assoc', cascade='save-update, merge, delete, delete-orphan'))
    course = relationship(Course, backref=backref(
        'inst_assoc', cascade='save-update, merge, delete, delete-orphan'))

    @staticmethod
    def find_association(db, user, course):
        return db.query(InstructorAssociation) \
            .filter_by(user=user, course=course).one_or_none()
