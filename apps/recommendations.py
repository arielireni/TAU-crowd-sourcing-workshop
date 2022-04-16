from sqlalchemy.orm import aliased

from apps.authentication.models import *

num_recommendations = 5
thres = 0  # we will not consider users with less than this number of courses that current user has taken


def get_closest_users(curr_user: Users):
    candidates = {}
    UC1 = aliased(UsersCourses)
    similar_courses = db.session.query(UsersCourses, UC1).join(UC1, UsersCourses.course_id == UC1.course_id).filter(
        UsersCourses.user_id == curr_user.id, UsersCourses.status == 2, UC1.status == 2).all()
    print(similar_courses)
    print(len(similar_courses))
    for pair in similar_courses:
        if pair[1].user_id not in candidates:
            candidates[pair[1].user_id] = (0, 0)  # first is sum of rating diff, second is number of courses
            candidates[pair[1].user_id] = (abs(pair[0].rating - pair[1].rating), 1)
        else:
            candidates[pair[1].user_id] = (
                candidates[pair[1].user_id][0] + abs(pair[0].rating - pair[1].rating),
                candidates[pair[1].user_id][1] + 1)
    closest_users = [(user_id, candidates[user_id][0] / candidates[user_id][1]) for user_id in candidates if
                     candidates[user_id][1] >= thres]
    closest_users.sort(key=lambda x: x[1])
    print(closest_users)
    return closest_users


# def get_highest_rated_untaken_courses(curr_user: Users, closest_users: list):
#     taken_courses = [course.course_id for course in curr_user.courses]
#     untaken_courses = Courses.query.filter(Courses.id.notin(taken_courses)).all()
#     for course in untaken_courses:
#
#     return untaken_courses[:num_recommendations]


def collaborative_filtering(curr_user: Users):
    closest_users = get_closest_users(curr_user)

    return closest_users


def recommend_courses(curr_user: Users):
    return collaborative_filtering(curr_user)
