# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for, render_template_string
from flask_login import current_user, login_required
from apps.authentication import blueprint
from apps.authentication.models import *


# @login_required
# @blueprint.route('course=<course_id>')
# def course(course_id):
#     course = Courses.query.filter_by(id=course_id).first()
#     answers = CoursesQuestions.query.filter_by(course_id=course_id).all()
#     comments = [comment for comment in Comments.query.filter_by(course_id=course_id).all()]
#     comments.sort(key=lambda x: x.time, reverse=True)
#     features = []
#     for answer in answers:
#         question_id = answer.question_id
#         question = Questions.query.filter_by(id=question_id).first()
#         features.append(('id' + str(question.id), question.feature, answer.sum_ratings / answer.num_ratings))
#     return render_template('home/course.html', course=course, featurs=features, comments=comments)


@login_required
@blueprint.route('course=<course_id>')
def course(course_id):
    course = Courses.query.filter_by(id=course_id).first()
    answers = CoursesQuestions.query.filter_by(course_id=course_id).all()
    comments = [comment for comment in Comments.query.filter_by(course_id=course_id).all()]
    comments.sort(key=lambda x: x.time, reverse=True)
    comments_likes = []
    comments_dislikes = []
    for comment in comments:
        user_comment = comment.users
        likes = [user.like_status for user in user_comment if user.like_status == 1]
        dislikes = [user.like_status for user in user_comment if user.like_status == 2]
        comments_likes.append(len(likes))
        comments_dislikes.append(len(dislikes))
    user_comment_data = [a for a in UsersComments.query.filter_by(course_id=course_id, user_id=current_user.id).all()]
    like_status = {a.comment_id: a.like_status for a in user_comment_data}
    thumb_colors = [['gray', 'gray'], ['green', 'gray'], ['gray', 'red']]
    features = []
    for answer in answers:
        question_id = answer.question_id
        question = Questions.query.filter_by(id=question_id).first()
        features.append(('id' + str(question.id), question.feature, answer.sum_ratings / answer.num_ratings))
    return render_template('home/course.html', course=course, featurs=features, comments=comments,
                           like_status=like_status, thumb_colors=thumb_colors, comments_likes=comments_likes,
                           comments_dislikes=comments_dislikes)


@login_required
@blueprint.route('course=<course_id>&like_comment=<comment_id>')
def like_comment(course_id, comment_id):
    user = current_user
    user_comment = UsersComments.query.filter_by(user_id=user.id, course_id=course_id, comment_id=comment_id).first()
    if user_comment is None:
        user_comment = UsersComments(user_id=user.id, course_id=course_id, is_author = False, comment_id=comment_id, like_status=1)
        db.session.add(user_comment)
        db.session.commit()
    else:
        if user_comment.like_status == 1:
            user_comment.like_status = 0
        else:
            user_comment.like_status = 1
        db.session.commit()
    return redirect(url_for('authentication_blueprint.course', course_id=course_id))


@login_required
@blueprint.route('course=<course_id>&dislike_comment=<comment_id>')
def dislike_comment(course_id, comment_id):
    user = current_user
    user_comment = UsersComments.query.filter_by(user_id=user.id, course_id=course_id, comment_id=comment_id).first()
    if user_comment is None:
        user_comment = UsersComments(user_id=user.id, course_id=course_id, is_author = False, comment_id=comment_id, like_status=-1)
        db.session.add(user_comment)
        db.session.commit()
    else:
        if user_comment.like_status == 2:
            user_comment.like_status = 0
        else:
            user_comment.like_status = 2
        db.session.commit()
    return redirect(url_for('authentication_blueprint.course', course_id=course_id))


@login_required
@blueprint.route('course=<course_id>', methods=['POST'])
def submit_comment(course_id):
    text = request.form['comment']
    user = current_user
    comment = Comments(comment=text, course_id=course_id, username=user.username)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('authentication_blueprint.course', course_id=course_id))
