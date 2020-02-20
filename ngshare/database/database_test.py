from database import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
def main():
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

    # check if values are sane
    print("List of users:")
    for i in db.query(User):
        print(i.id)
    print()

    print("User rkevin is teaching the courses:")
    user = db.query(User)\
        .filter(User.id == "rkevin")\
        .one_or_none()
    for i in user.teaching:
        print(i.id)

    print("In the 'ecs189m' class, there are these assignments:")
    course = db.query(Course)\
        .filter(Course.id == "ecs189m")\
        .one_or_none()
    for i in course.assignments:
        print("Assignment name:",i.id)
        print("There are",len(i.submissions),"submissions")
        for j in i.submissions:
            print("One submission from",j.student,"at",j.timestamp)

if __name__ == '__main__':
    main()
