# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import flask_login

from apps.authentication.models import *
from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import apps.recommendations as rs
import apps.questions as qs


@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('course=<course_id>')
def course(course_id):
    course = Courses.query.filter_by(id=course_id).first()
    answers = CoursesQuestions.query.filter_by(course_id=course_id).all()
    features = []
    for answer in answers:
        question_id = answer.question_id
        question = Questions.query.filter_by(id=question_id).first()
        features.append(('id' + str(question.id), question.feature, answer.sum_ratings / answer.num_ratings))
    return render_template('home/course.html', course=course, featurs=features)


@blueprint.route('/for-you.html')
def for_you():
    segment = get_segment(request)
    return render_template("home/" + 'for-you.html', segment=segment,
                           courses=rs.recommend_courses(flask_login.current_user))


@blueprint.route('/game.html')
def game():
    segment = get_segment(request)
    return render_template('home/' + 'game.html', segment=segment, questions_to_review=qs.get_questions())


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
