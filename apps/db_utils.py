from authentication import models
from sqlalchemy.orm import Session
from apps import db


def trying():
    with Session(db.engine) as session:
        algo = models.Courses(name="Algorithms")
        rani = models.Lecturers(name="Rani Hod", avg_rating=5, num_ratings=1)
        rani_algo = models.CoursesLecturers(course_id=algo.id, lecturer_id=rani.id, year=2022, semester=0)
        rani_algo.course = algo
        rani_algo.lecturer = rani
        session.add_all([algo, rani, rani_algo])
        session.commit()


if __name__ == '__main__':
    trying()
