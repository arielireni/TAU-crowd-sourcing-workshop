from apps.authentication.models import *
from math import sqrt


def search_course(category, search_string):
    if category == 'Lecturer':
        qry = db.session.query(Courses, CoursesLecturers, Lecturers).join(Courses,
            Courses.id == CoursesLecturers.course_id).join(Lecturers,
            Lecturers.id == CoursesLecturers.lecturer_id).filter(Lecturers.name.contains(search_string)).distinct()
        results = [item[0] for item in qry.all()]
    elif category == 'Course':
        qry = db.session.query(Courses).filter(
            Courses.name.contains(search_string))
        results = qry.all()
    elif category == 'Course Number':
        qry = db.session.query(Courses).filter(
            Courses.id.contains(search_string))
        results = qry.all()
    else:
        qry = db.session.query(Courses)
        results = qry.all()
    return results


def calculate_norm(ratings, course_ratings):
    norm = 0
    print(ratings)
    print(course_ratings)
    for tup in ratings:
        norm += pow((tup[1] - course_ratings[tup[0]]), 2)
    return sqrt(norm)

def get_closest_courses(ratings, results):

    # ratings - the ratings the user asked to filter by
    # results - a table of courses resulted in the course/lecturer search

    first_id = db.session.query(Questions).first().id
    norms=[]
    for course in results:
        my_questions = course.questions
        course_ratings = [0 for q in my_questions]
        for q in my_questions:
            course_ratings[q.question_id - first_id] = q.sum_ratings/q.num_ratings
        norms.append((course, calculate_norm(ratings,course_ratings)))
    norms.sort(key=lambda y:y[1], reverse=False)
    return [x[0] for x in norms]