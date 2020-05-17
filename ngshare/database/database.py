'''
    Database structure for NGShare
'''

import datetime
import hashlib

from sqlalchemy import (
    Table,
    Column,
    INTEGER,
    TEXT,
    TIMESTAMP,
    BOOLEAN,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Assignment -> Course (One to Many)
assignment_files_assoc_table = Table(
    'assignment_files_assoc_table',
    Base.metadata,
    Column('left_id', TEXT, ForeignKey('assignments._id'), primary_key=True),
    Column('right_id', INTEGER, ForeignKey('files._id'), primary_key=True),
)

# Submission -> Course (One to Many)
submission_files_assoc_table = Table(
    'submission_files_assoc_table',
    Base.metadata,
    Column('left_id', TEXT, ForeignKey('submissions._id'), primary_key=True),
    Column('right_id', INTEGER, ForeignKey('files._id'), primary_key=True),
)

# Submission (feedback) -> Course (One to Many)
feedback_files_assoc_table = Table(
    'feedback_files_assoc_table',
    Base.metadata,
    Column('left_id', TEXT, ForeignKey('submissions._id'), primary_key=True),
    Column('right_id', INTEGER, ForeignKey('files._id'), primary_key=True),
)


class User(Base):
    'A JupyterHub user; can be either instructor or student, or both'
    __tablename__ = 'users'
    id = Column(TEXT, primary_key=True)
    teaching = association_proxy(
        'inst_assoc',
        'course',
        creator=lambda course: InstructorAssociation(course=course),
        cascade_scalar_deletes=True,
    )
    taking = association_proxy(
        'student_assoc',
        'course',
        creator=lambda course: StudentAssociation(course=course),
        cascade_scalar_deletes=True,
    )

    def __init__(self, name):
        'Initialize with JupyterHub user name'
        self.id = name

    def __str__(self):
        return '<User %s>' % self.id

    def dump(self):
        'Dump data to dict'
        return {
            'id': self.id,
        }

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
    instructors = association_proxy(
        'inst_assoc',
        'user',
        creator=lambda user: InstructorAssociation(user=user,),
        cascade_scalar_deletes=True,
    )
    students = association_proxy(
        'student_assoc',
        'user',
        creator=lambda user: StudentAssociation(user=user,),
        cascade_scalar_deletes=True,
    )
    assignments = relationship('Assignment', backref='course')

    def dump(self):
        'Dump data to dict'
        return {
            '_id': self._id,
            'id': self.id,
        }

    def __init__(self, name, instructors=()):
        'Initialize with course name and teacher'
        self.id = name
        for instructor in instructors:
            self.instructors.append(instructor)

    def __str__(self):
        return '<Course %s>' % self.id

    def delete(self, db):
        'Remove course and dependent data'
        for assignment in self.assignments:
            assignment.delete(db)
        for student in self.students[:]:
            self.students.remove(student)
        for instructor in self.instructors[:]:
            self.instructors.remove(instructor)
        db.delete(self)


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

    def dump(self):
        'Dump data to dict'
        return {
            '_id': self._id,
            'id': self.id,
            'course_id': self.course_id,
            'released': bool(self.released),
            'due': self.due and self.due.strftime('%Y-%m-%d %H:%M:%S.%f %Z'),
        }

    def delete(self, db):
        'Remove assignment and dependent data (files, submissions)'
        for file_obj in self.files[:]:
            file_obj.delete(db)
            self.files.remove(file_obj)
        for submission in self.submissions[:]:
            submission.delete(db)
            self.submissions.remove(submission)
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
        self.timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.student = student
        self.assignment = assignment

    def __str__(self):
        return '<Submission %d>' % self._id

    def dump(self):
        'Dump data to dict'
        return {
            '_id': self._id,
            'assignment_id': self.assignment_id,
            'timestamp': self.timestamp
            and self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f %Z'),
            'student_id': self.student_id,
        }

    def delete(self, db):
        'Remove submission and dependent data (files, feedbacks)'
        for file_obj in self.files[:]:
            file_obj.delete(db)
            self.files.remove(file_obj)
        for file_obj in self.feedbacks[:]:
            file_obj.delete(db)
            self.feedbacks.remove(file_obj)
        db.delete(self)


class File(Base):
    'A File (for assignment, submission file, or submission feedback)'
    __tablename__ = 'files'
    _id = Column(INTEGER, primary_key=True)
    filename = Column(TEXT)
    checksum = Column(TEXT)
    size = Column(INTEGER)
    actual_name = Column(TEXT)

    def __init__(self, filename, contents, actual_name=None):
        'Initialize with file name and content; auto-compute md5 and size'
        self.filename = filename
        self.checksum = hashlib.md5(contents).hexdigest()
        self.size = len(contents)
        self.actual_name = actual_name

    def __str__(self):
        return '<File %s>' % self.filename

    def dump(self):
        'Dump data to dict'
        return {
            '_id': self._id,
            'filename': self.filename,
            'checksum': self.checksum,
            'size': self.size,
            'actual_name': self.actual_name,
        }

    def delete(self, db):
        'Remove file'
        db.delete(self)


# Ref: https://stackoverflow.com/a/7524753
# Ref: https://stackoverflow.com/a/23734727
class InstructorAssociation(Base):
    'Relationship between instructor and course, many to many, with extra data'
    __tablename__ = 'instructor_assoc_table'
    left_id = Column(TEXT, ForeignKey('users.id'), primary_key=True)
    right_id = Column(TEXT, ForeignKey('courses.id'), primary_key=True)
    first_name = Column(TEXT)
    last_name = Column(TEXT)
    email = Column(TEXT)
    user = relationship(
        User,
        backref=backref(
            'inst_assoc', cascade='save-update, merge, delete, delete-orphan'
        ),
    )
    course = relationship(
        Course,
        backref=backref(
            'inst_assoc', cascade='save-update, merge, delete, delete-orphan'
        ),
    )

    @staticmethod
    def find(db, instructor, course):
        'Find association object from user and course'
        return (
            db.query(InstructorAssociation)
            .filter_by(user=instructor, course=course)
            .one_or_none()
        )

    def dump(self):
        'Dump data to dict'
        return {
            'left_id': self.left_id,
            'right_id': self.right_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
        }


# Student -> Course (Many to Many)
class StudentAssociation(Base):
    'Relationship between student and course, many to many, with extra data'
    __tablename__ = 'student_assoc_table'
    left_id = Column(TEXT, ForeignKey('users.id'), primary_key=True)
    right_id = Column(TEXT, ForeignKey('courses.id'), primary_key=True)
    first_name = Column(TEXT)
    last_name = Column(TEXT)
    email = Column(TEXT)
    user = relationship(
        User,
        backref=backref(
            'student_assoc', cascade='save-update, merge, delete, delete-orphan'
        ),
    )
    course = relationship(
        Course,
        backref=backref(
            'student_assoc', cascade='save-update, merge, delete, delete-orphan'
        ),
    )

    @staticmethod
    def find(db, student, course):
        'Find association object from user and course'
        return (
            db.query(StudentAssociation)
            .filter_by(user=student, course=course)
            .one_or_none()
        )

    def dump(self):
        'Dump data to dict'
        return {
            'left_id': self.left_id,
            'right_id': self.right_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
        }
