from sqlalchemy.orm import aliased
from apps.authentication.models import *


def get_closest_users(curr_user: Users, k, thres):
    """ Returns a list of tuples of the form (user_id, avg_rating_diff), sorted by avg_rating_diff, for user_ids that
     have at least thres number of courses that current user has taken. """
    candidates = {}
    UC1 = aliased(UsersCourses)
    similar_courses = db.session.query(UsersCourses, UC1).join(UC1, UsersCourses.course_id == UC1.course_id).filter(
        UsersCourses.user_id == curr_user.id, UC1.user_id != curr_user.id).all()
    for pair in similar_courses:
        if pair[1].user_id not in candidates:
            print(pair)
            candidates[pair[1].user_id] = (0, 0)  # first is sum of rating diff, second is number of courses
            candidates[pair[1].user_id] = (abs(pair[0].rating - pair[1].rating), 1)
        else:
            candidates[pair[1].user_id] = (
                candidates[pair[1].user_id][0] + abs(pair[0].rating - pair[1].rating),
                candidates[pair[1].user_id][1] + 1)
    closest_users = [(user_id, candidates[user_id][0] / candidates[user_id][1]) for user_id in candidates if
                     candidates[user_id][1] >= thres]
    closest_users.sort(key=lambda x: x[1])
    return closest_users[:k]


def get_highest_rated_untaken_courses(curr_user: Users, closest_users: list):
    """" Returns a list of untaken courses sorted by the highest average rating from closest_users, descending. """
    taken_courses = [course.course_id for course in curr_user.courses]
    untaken_courses = Courses.query.filter(Courses.id.notin_(taken_courses)).all()
    closest_users_opinions = UsersCourses.query.filter(UsersCourses.user_id.in_(closest_users),
                                                       ).all()
    untaken_courses = {course.id: (course, 0, 0) for course in
                       untaken_courses}  # first is course, second is sum of ratings, third is number of ratings
    for opinion in closest_users_opinions:
        if opinion.course_id in untaken_courses:
            untaken_courses[opinion.course_id] = (
                untaken_courses[opinion.course_id][0], untaken_courses[opinion.course_id][1] + opinion.rating,
                untaken_courses[opinion.course_id][2] + 1)
    untaken_courses = sorted([a for a in untaken_courses.values() if a[2] > 0], key=lambda x: x[1] / x[2], reverse=True)
    return untaken_courses


def collaborative_filtering(curr_user: Users, k=5, thres=0, num_recommendations=5):
    """ returns a list of course recommendations for curr_user, based on the ratings of the k closest users to him
    (from these who took at least thres courses that curr_user took) on courses that he has not taken. """
    closest_users = get_closest_users(curr_user, k, thres)
    # print(closest_users)
    recommendations = get_highest_rated_untaken_courses(curr_user, [pair[0] for pair in closest_users])
    # print(recommendations)
    # return [a[0] for a in recommendations[:num_recommendations]]
    return recommendations[:num_recommendations]


def recommend_courses(curr_user: Users):
    num_users = Users.query.count()
    return collaborative_filtering(curr_user, k=int(num_users / 10), thres=2, num_recommendations=5)
