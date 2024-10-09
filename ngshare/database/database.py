'''
    Database structure for NGShare
'''

import datetime
import hashlib

from sqlalchemy import (
    Table,
    Column,
    Integer,
    Text,
    TIMESTAMP,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base, Mapped
from sqlalchemy.ext.associationproxy import association_proxy

from typing import List

Base = declarative_base()

# Assignment -> Course (One to Many)
assignment_files_assoc_table = Table(
    'assignment_files_assoc_table',
    Base.metadata,
    Column('left_id', Text, ForeignKey('assignments._id'), primary_key=True),
    Column('right_id', Integer, ForeignKey('files._id'), primary_key=True),
)

# Submission -> Course (One to Many)
submission_files_assoc_table = Table(
    'submission_files_assoc_table',
    Base.metadata,
    Column('left_id', Text, ForeignKey('submissions._id'), primary_key=True),
    Column('right_id', Integer, ForeignKey('files._id'), primary_key=True),
)

# Submission (feedback) -> Course (One to Many)
feedback_files_assoc_table = Table(
    'feedback_files_assoc_table',
    Base.metadata,
    Column('left_id', Text, ForeignKey('submissions._id'), primary_key=True),
    Column('right_id', Integer, ForeignKey('files._id'), primary_key=True),
)


class User(Base):
    'A JupyterHub user; can be either instructor or student, or both'
    __tablename__ = 'users'
    id = Column(Text, primary_key=True)
    teaching: Mapped[List['Course']] = association_proxy(
        'inst_assoc',
        'course',
        creator=lambda course: InstructorAssociation(course=course),
        cascade_scalar_deletes=True,
    )
    inst_assoc: Mapped[List['InstructorAssociation']] = relationship(
        'InstructorAssociation',
        back_populates='user',
        cascade='save-update, merge, delete, delete-orphan',
    )
    taking: Mapped[List['Course']] = association_proxy(
        'student_assoc',
        'course',
        creator=lambda course: StudentAssociation(course=course),
        cascade_scalar_deletes=True,
    )
    student_assoc: Mapped[List['StudentAssociation']] = relationship(
        'StudentAssociation',
        back_populates='user',
        cascade='save-update, merge, delete, delete-orphan',
    )

    def __init__(self, name):
        'Initialize with JupyterHub user name'
        self.id = name

    def __str__(self):
        return '<User %s>' % self.id

    def dump(self) -> dict:
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
    _id = Column(Integer, primary_key=True)
    id = Column(Text, unique=True)
    instructors: Mapped[List['User']] = association_proxy(
        'inst_assoc',
        'user',
        creator=lambda user: InstructorAssociation(
            user=user,
        ),
        cascade_scalar_deletes=True,
    )
    inst_assoc: Mapped[List['InstructorAssociation']] = relationship(
        'InstructorAssociation',
        back_populates='course',
        cascade='save-update, merge, delete, delete-orphan',
    )
    students: Mapped[List['User']] = association_proxy(
        'student_assoc',
        'user',
        creator=lambda user: StudentAssociation(
            user=user,
        ),
        cascade_scalar_deletes=True,
    )
    student_assoc: Mapped[List['StudentAssociation']] = relationship(
        'StudentAssociation',
        back_populates='course',
        cascade='save-update, merge, delete, delete-orphan',
    )
    assignments = relationship('Assignment', back_populates='course')

    def dump(self) -> dict:
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
    _id = Column(Integer, primary_key=True)
    id = Column(Text)
    course_id = Column(Integer, ForeignKey('courses._id'))
    course = relationship('Course', back_populates='assignments')
    submissions = relationship('Submission', back_populates='assignment')
    files = relationship('File', secondary=assignment_files_assoc_table)
    released = False
    due = Column(TIMESTAMP)
    # TODO: timezoon

    def __init__(self, name, course):
        'Initialize with assignment name and course'
        self.id = name
        self.course = course

    def __str__(self):
        return '<Assignment %s>' % self.id

    def dump(self) -> dict:
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
    _id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('assignments._id'))
    assignment = relationship('Assignment', back_populates='submissions')
    timestamp = Column(TIMESTAMP)
    student_id = Column(Text, ForeignKey('users.id'))
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

    def dump(self) -> dict:
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
    _id = Column(Integer, primary_key=True)
    filename = Column(Text)
    checksum = Column(Text)
    size = Column(Integer)
    actual_name = Column(Text)

    def __init__(self, filename, contents, actual_name=None):
        'Initialize with file name and content; auto-compute md5 and size'
        self.filename = filename
        self.checksum = hashlib.md5(contents).hexdigest()
        self.size = len(contents)
        self.actual_name = actual_name

    def __str__(self):
        return '<File %s>' % self.filename

    def dump(self) -> dict:
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
    left_id = Column(Text, ForeignKey('users.id'), primary_key=True)
    right_id = Column(Text, ForeignKey('courses.id'), primary_key=True)
    first_name = Column(Text)
    last_name = Column(Text)
    email = Column(Text)
    user = relationship(
        User,
        back_populates='inst_assoc',
    )
    course = relationship(
        Course,
        back_populates='inst_assoc',
    )

    @staticmethod
    def find(db, instructor, course):
        'Find association object from user and course'
        return (
            db.query(InstructorAssociation)
            .filter_by(user=instructor, course=course)
            .one_or_none()
        )

    def dump(self) -> dict:
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
    left_id = Column(Text, ForeignKey('users.id'), primary_key=True)
    right_id = Column(Text, ForeignKey('courses.id'), primary_key=True)
    first_name = Column(Text)
    last_name = Column(Text)
    email = Column(Text)
    user = relationship(
        User,
        back_populates='student_assoc',
    )
    course = relationship(
        Course,
        back_populates='student_assoc',
    )

    @staticmethod
    def find(db, student, course):
        'Find association object from user and course'
        return (
            db.query(StudentAssociation)
            .filter_by(user=student, course=course)
            .one_or_none()
        )

    def dump(self) -> dict:
        'Dump data to dict'
        return {
            'left_id': self.left_id,
            'right_id': self.right_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
        }
