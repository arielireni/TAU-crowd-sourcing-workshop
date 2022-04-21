# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json
from apps.home.routes import get_segment
from flask import render_template, request
from apps.authentication import blueprint
from apps.authentication.models import *


@blueprint.route('/game.html', methods=['GET', 'POST'])
def game():
    segment = get_segment(request)
    questions = Questions.query.all()
    courses = Courses.query.all()
    num_questions = len(questions)
    # TODO: use this value for submit_user_ratings
    if request.method == 'POST':
        course = request.form.get('course')
    return render_template('home/' + 'game.html', segment=segment, questions=questions, num_questions=num_questions,
                           courses=courses)


@blueprint.route('/submit_user_ratings/<string:ratings>', methods=['POST'])
def submit_user_ratings(ratings):
    ratings = json.loads(ratings)
    # TODO: replace with db update
    for i in range(len(ratings)):
        question_id = ratings[i][0]
        rate = ratings[i][1]
    return "Ratings received!"

