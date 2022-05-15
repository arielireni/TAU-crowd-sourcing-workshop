# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json
from flask_login import login_required, current_user
from apps.home.routes import get_segment
from flask import render_template, request, url_for, redirect
from apps.authentication.models import *
from apps.game import blueprint


@login_required
@blueprint.route('/game.html', methods=['GET', 'POST'])
def game():
    segment = get_segment(request)
    questions = Questions.query.all()
    num_questions = len(questions)
    user = current_user
    # Rate only undone courses
    taken_courses = set([usercourse.course.id for usercourse in UsersCourses.query.filter_by(user_id=user.id).all()])
    untaken_courses = Courses.query.filter(~Courses.id.in_(taken_courses)).all()

    return render_template('home/' + 'game.html', segment=segment, questions=questions, num_questions=num_questions,
                           courses=untaken_courses)


@login_required
@blueprint.route('/get_game_details/<string:details>', methods=['GET', 'POST'])
def get_game_details(details):
    details = json.loads(details)
    selected_course = details[len(details) - 2][1]
    # Update ratings and calculate average rating
    num_questions = len(details) - 2
    sum_ratings = 0

    for i in range(num_questions):
        if i == num_questions - 1:
            overall_rating = details[i][1]
            continue
        question_id = details[i][0]
        rate = details[i][1]
        sum_ratings += rate
        course = Courses.query.filter_by(name=selected_course).first()
        question_rate = CoursesQuestions.query.filter_by(course_id=course.id, question_id=question_id).first()
        if question_rate is None:
            question_rate = CoursesQuestions(course_id=course.id, question_id=question_id, sum_ratings=rate,
                                             num_ratings=1)
            db.session.add(question_rate)

        else:
            question_rate.sum_ratings += rate
            question_rate.num_ratings += 1

    user = current_user

    # Mark course as done after summiting the ratings
    done_course = UsersCourses(user_id=user.id, course_id=course.id, rating=overall_rating)
    db.session.add(done_course)

    # Update user credits
    user.credits += course.credit_points

    # Update best score if needed
    game_score = details[len(details) - 1][1]
    if game_score > user.best_score:
        user.best_score = game_score

    db.session.commit()

    return "details submitted!"


@login_required
@blueprint.route('/high-scores.html', methods=['GET'])
def high_scores():
    best_scores = Users.query.order_by(Users.best_score).all()[-10:]
    best_scores = [result for result in best_scores if result.best_score != 0]

    return render_template('home/' + 'high-scores.html', best_scores=best_scores)
