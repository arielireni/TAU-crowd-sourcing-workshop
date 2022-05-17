import flask_login
from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import apps.for_you.recommendations as rs
from apps.home.routes import get_segment


@blueprint.route('/for-you.html')
def for_you():
    segment = get_segment(request)
    courses = rs.recommend_courses(flask_login.current_user)
    # get the highest rated question and the lowest rated question for each course in courses
    questions = []
    for course in courses:
        course = course[0]
        course_questions = course.questions
        course_questions = sorted(course_questions, key=lambda x: x.sum_ratings / x.num_ratings)
        questions.append((course_questions[-1], course_questions[0]))
    return render_template("home/" + 'for-you.html', segment=segment,
                           courses=courses,
                           round=round,
                           best_worst_questions=questions)
