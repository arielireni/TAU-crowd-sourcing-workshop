from flask import render_template, redirect, request, url_for, render_template_string, jsonify
from flask_login import current_user, login_required
from apps.course_page import blueprint
from apps.authentication.models import *


def get_like_info(comment: Comments):
    user_comment = comment.users
    likes = [user.like_status for user in user_comment if user.like_status == 1]
    dislikes = [user.like_status for user in user_comment if user.like_status == 2]
    return len(likes), len(dislikes)


@login_required
@blueprint.route('course=<course_id>')
def course(course_id):
    print([a.course_id for a in current_user.taudata_courses])
    course = Courses.query.filter_by(id=course_id).first()
    answers = CoursesQuestions.query.filter_by(course_id=course_id).all()
    comments = [comment for comment in Comments.query.filter_by(course_id=course_id).all()]
    comments_likes = []  # comments_likes[i] = #likes of comments[i]
    comments_dislikes = []  # comments_dislikes[i] = #dislikes of comments[i]
    for comment in comments:
        likes, dislikes = get_like_info(comment)
        comments_likes.append(likes)
        comments_dislikes.append(dislikes)
    comments = [(comments[i], comments_likes[i], comments_dislikes[i]) for i in range(len(comments))]
    comments.sort(key=lambda x: x[1] - x[2], reverse=True)  # sort comments by likes-dislikes
    comments_likes = [comment[1] for comment in comments]
    comments_dislikes = [comment[2] for comment in comments]
    comments = [comment[0] for comment in comments]
    # for each comment in this page, determine if the user likes/dislikes it or neither
    user_comment_data = [a for a in UsersComments.query.filter_by(course_id=course_id, user_id=current_user.id).all()]
    # like_status value is 0 for neither, 1 for like and 2 for dislike
    like_status = {a.comment_id: a.like_status for a in user_comment_data}
    thumb_colors = [['gray', 'gray'], ['green', 'gray'], ['gray', 'red']]
    features = []
    for answer in answers:
        question_id = answer.question_id
        question = Questions.query.filter_by(id=question_id).first()
        features.append(('id' + str(question.id), question.feature, answer.sum_ratings / answer.num_ratings))
    taken_courses = [a.course_id for a in current_user.taudata_courses]
    print(taken_courses)
    return render_template('home/course.html', course=course, featurs=features, comments=comments,
                           like_status=like_status, thumb_colors=thumb_colors, comments_likes=comments_likes,
                           comments_dislikes=comments_dislikes, round=round, taken_courses=taken_courses)


# this function is called when the user clicks on the like button via ajax
@login_required
@blueprint.route('background_like/course=<course_id>&comment=<comment_id>')
def like_comment(course_id, comment_id):
    like_color = 'green'
    user = current_user
    user_comment = UsersComments.query.filter_by(user_id=user.id, course_id=course_id, comment_id=comment_id).first()
    comment = Comments.query.filter_by(id=comment_id).first()
    if user_comment is None:
        user_comment = UsersComments(user_id=user.id, course_id=course_id, is_author=False, comment_id=comment_id,
                                     like_status=1)
        db.session.add(user_comment)
        db.session.commit()
    else:
        if user_comment.like_status == 1:
            user_comment.like_status = 0
            like_color = 'gray'
        else:
            user_comment.like_status = 1
        db.session.commit()
    likes, dislikes = get_like_info(comment)
    return jsonify({'likes': likes, 'dislikes': dislikes, 'like_color': like_color})


# this function is called when the user clicks on the dislike button via ajax
@login_required
@blueprint.route('background_dislike/course=<course_id>&comment=<comment_id>')
def dislike_comment(course_id, comment_id):
    dislike_color = 'red'
    user = current_user
    user_comment = UsersComments.query.filter_by(user_id=user.id, course_id=course_id, comment_id=comment_id).first()
    comment = Comments.query.filter_by(id=comment_id).first()
    if user_comment is None:
        user_comment = UsersComments(user_id=user.id, course_id=course_id, is_author=False, comment_id=comment_id,
                                     like_status=2)
        db.session.add(user_comment)
        db.session.commit()
    else:
        if user_comment.like_status == 2:
            user_comment.like_status = 0
            dislike_color = 'gray'
        else:
            user_comment.like_status = 2
        db.session.commit()
    likes, dislikes = get_like_info(comment)
    return jsonify({'likes': likes, 'dislikes': dislikes, 'dislike_color': dislike_color})


@login_required
@blueprint.route('course=<course_id>', methods=['POST'])
def submit_comment(course_id):
    text = request.form['comment']
    user = current_user
    comment = Comments(comment=text, course_id=course_id, username=user.username)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('coursepage_blueprint.course', course_id=course_id))
