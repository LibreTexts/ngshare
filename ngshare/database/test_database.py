'''
    Test database structure and some properties of SQLAlchemy
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# pylint: disable=global-statement
# pylint: disable=invalid-name
# pylint: disable=len-as-condition
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import

Session = None

try:
    from .database import *
except ImportError:
    from database import *

def clear_db(db):
    'Remove all data from database'
    db.query(User).delete()
    db.query(Course).delete()
    db.query(Assignment).delete()
    db.query(Submission).delete()
    db.query(File).delete()
    for table_name in [
            'instructor_assoc_table',
            'student_assoc_table',
            'assignment_files_assoc_table',
            'submission_files_assoc_table',
            'feedback_files_assoc_table',
        ]:
        db.execute('DELETE FROM %s' % table_name)
    db.commit()

def init_db(db):
    '''
        Create testing data
        course1
            instructor = [kevin]
            student = [lawrence]
            assignments = [challenge] (two submissions, one feedback)
        course2
            instructor = [abigail]
            student = [eric]
            assignments = [assignment2a, assignment2b] (no submissions)
    '''
    uk = User('kevin')
    ua = User('abigail')
    ul = User('lawrence')
    ue = User('eric')
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
    db.add(s1)
    db.add(s2)
    aa.files.append(File('file0', b'00000'))
    ab.files.append(File('file1', b'11111'))
    ac.files.append(File('file2', b'22222'))
    s1.files.append(File('file3', b'33333'))
    s2.files.append(File('file4', b'44444'))
    s1.feedbacks.append(File('file5', b'55555'))
    db.commit()

def test_legacy():
    'Some test cases created when building database structure'
    global Session
    engine = create_engine('sqlite://') # temp database in memory
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # populate with random data
    instructor = User("rkevin")
    student = User("rk-test")
    db.add(instructor)
    db.add(student)
    course = Course("ecs189m", instructor)
    assignment = Assignment("ps1", course)
    submission = Submission(student, assignment)
    db.add(course)
    db.commit()
    print(submission)

    # check if values are sane
    print("List of users:")
    for i in db.query(User):
        print(i.id)
    print()

    print("User rkevin is teaching the courses:")
    user = db.query(User).filter(User.id == "rkevin").one_or_none()
    for i in user.teaching:
        print(i.id)

    print("In the 'ecs189m' class, there are these assignments:")
    course = db.query(Course).filter(Course.id == "ecs189m").one_or_none()
    for i in course.assignments:
        print("Assignment name:", i.id)
        print("There are", len(i.submissions), "submissions")
        for j in i.submissions:
            print("One submission from", j.student, "at", j.timestamp)

def test_init():
    'Test clearing database and fill in default test data'
    db = Session()
    clear_db(db)
    assert not db.query(InstructorAssociation).all()
    assert not db.query(student_assoc_table).all()
    assert not db.query(assignment_files_assoc_table).all()
    assert not db.query(submission_files_assoc_table).all()
    assert not db.query(feedback_files_assoc_table).all()
    assert not db.query(User).all()
    assert not db.query(Course).all()
    assert not db.query(Assignment).all()
    assert not db.query(Submission).all()
    assert not db.query(File).all()
    init_db(db)
    assert len(db.query(User).all()) == 4
    assert len(db.query(Course).all()) == 2
    assert len(db.query(Assignment).all()) == 3
    assert len(db.query(Submission).all()) == 2
    assert len(db.query(File).all()) == 6

def test_upload_feedback():
    'When uploading feedback, old feedbacks need to be removed'
    db = Session()
    ts = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
    s1 = db.query(Submission).filter(Submission.timestamp == ts).one_or_none()
    assert s1 is not None
    assert len(s1.feedbacks) == 1
    for file in s1.feedbacks:
        db.delete(file)
    s1.feedbacks.clear()
    db.commit()
    assert len(db.query(File).all()) == 5

def test_remove_assignment():
    'Test when removing assignment, submissions and files need to be removed'
    db = Session()
    ac = db.query(Assignment).filter(Assignment.id == 'challenge').one_or_none()
    assert ac is not None
    ac.delete(db)
    db.commit()
    assert len(db.query(Assignment).all()) == 2
    assert len(db.query(Submission).all()) == 0
    assert len(db.query(File).all()) == 2

def test_assoc_table_extra_data():
    'Test accessing extra data (full name, email) from association table'
    db = Session()
    kevin = db.query(User).first()
    assert kevin.id == 'kevin'
    assert len(kevin.teaching) == 1
    course1 = kevin.teaching[0]
    assert course1.id == 'course1'
    relation_count = len(db.query(InstructorAssociation).all())
    # Check relation
    kevin.teaching.remove(kevin.teaching[0])
    db.commit()
    assert len(course1.instructors) == 0
    assert len(db.query(InstructorAssociation).all()) == relation_count - 1
    course1.instructors.append(kevin)
    db.commit()
    assert len(db.query(InstructorAssociation).all()) == relation_count
    assert len(kevin.teaching) == 1
    # Check data
    association = InstructorAssociation.find_association(db, kevin, course1)
    assert association.first_name == '0/0'
    assert association.last_name == '0/0'
    assert association.email == '0/0'
