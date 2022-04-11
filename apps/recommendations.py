from apps.authentication.models import *

num_recommendations = 5


def recommend_courses():
    return Courses.query.all()
