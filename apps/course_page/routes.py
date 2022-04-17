# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for
from apps.authentication import blueprint
from apps.authentication.models import *

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
