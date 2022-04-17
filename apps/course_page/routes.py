# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for, render_template_string
from flask_login import current_user, login_required
from apps.authentication import blueprint
from apps.authentication.models import *


@login_required
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


@login_required
@blueprint.route('course=<course_id>', methods=['POST'])
def submit_comment(course_id):
    text = request.form['comment']
    user = current_user
    comment = Comments(comment=text, user_id=user.id, course_id=course_id)
    db.session.add(comment)
    db.session.commit()
    return course(course_id)


    # id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    # course_id = db.Column(db.Integer, db.ForeignKey('Courses.id'))
    # comment = db.Column(db.String(500), nullable=False)
    # likes = db.Column(db.Integer, default=0)
    # dislikes = db.Column(db.Integer, default=0)
    # time = db.Column(db.DateTime, default=func.now())