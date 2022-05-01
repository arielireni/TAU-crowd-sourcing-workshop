# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json
from flask_login import login_required, current_user
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
    best_scores = Users.query.order_by(Users.best_score).all()[-10:]
    if request.method == 'POST':
            return render_template('home/' + 'game.html', segment=segment, questions=questions, num_questions=num_questions,
                           courses=courses, best_scores=best_scores)

    return render_template('home/' + 'game_openpage.html', segment=segment, questions=questions, num_questions=num_questions,
                           courses=courses, best_scores=best_scores)


@login_required
@blueprint.route('/get_game_details/<string:details>', methods=['POST'])
def get_game_details(details):
    details = json.loads(details)
    selected_course = details[len(details) - 2][1]
    # Update ratings
    for i in range(len(details) - 2):
        question_id = details[i][0]
        rate = details[i][1]
        course = Courses.query.filter_by(name=selected_course).first()
        question_rate = CoursesQuestions.query.filter_by(course_id=course.id, question_id=question_id).first()
        if question_rate is None:
            question_rate = CoursesQuestions(course_id=course.id, question_id=question_id, sum_ratings=rate,
                                             num_ratings=1)
            db.session.add(question_rate)

        else:
            question_rate.sum_ratings += rate
            question_rate.num_ratings += 1

        db.session.commit()

    # Update best score if needed
    game_score = details[len(details) - 1][1]
    user = current_user
    if game_score > user.best_score:
        user.best_score = game_score
        db.session.commit()


   #return render_template('home/' + 'game_over.html')
    return "Details received!"

@blueprint.route('/gameover.html', methods=['GET', 'POST'])
def gameover():
    return render_template('home/' + 'game_over.html')