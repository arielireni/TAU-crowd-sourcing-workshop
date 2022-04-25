# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy.sql import func
from apps import db, login_manager

from apps.authentication.util import hash_pass


class UsersCourses(db.Model):
    __tablename__ = 'UsersCourses'
    user_id = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    course_id = db.Column(db.ForeignKey('Courses.id'), primary_key=True)
    rating = db.Column(db.SMALLINT, default=-1)  # -1 for not rated yet
    user = db.relationship("Users", back_populates="courses")
    course = db.relationship("Courses", back_populates="users")

    def __repr__(self):
        return f'user {self.user_id} has taken course {self.course_id}'


class CoursesQuestions(db.Model):
    __tablename__ = 'CoursesQuestions'
    course_id = db.Column(db.ForeignKey('Courses.id'), primary_key=True)
    question_id = db.Column(db.ForeignKey('Questions.id'), primary_key=True)
    sum_ratings = db.Column(db.Integer, default=0)
    num_ratings = db.Column(db.Integer, default=0)
    course = db.relationship("Courses", back_populates="questions")
    question = db.relationship("Questions", back_populates="courses")

    def __repr__(self):
        return f'avg answer for course {self.course_id} for question {self.question_id}: {self.sum_ratings / self.num_ratings}'


class CoursesLecturers(db.Model):
    __tablename__ = 'CoursesLecturers'
    course_id = db.Column(db.ForeignKey('Courses.id'), primary_key=True)
    lecturer_id = db.Column(db.ForeignKey('Lecturers.id'), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.SMALLINT, primary_key=True)  # 0 for a, 1 for b, 2 for summer
    course = db.relationship("Courses", back_populates="lecturers")
    lecturer = db.relationship("Lecturers", back_populates="courses")

    def __repr__(self):
        return f'{self.lecturer.name} lectured {self.course.name} in {self.year}'


class UsersComments(db.Model):
    __tablename__ = 'UsersComments'
    user_id = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    comment_id = db.Column(db.ForeignKey('Comments.id'), primary_key=True)
    course_id = db.Column(db.ForeignKey('Courses.id'))
    is_author = db.Column(db.Boolean, nullable=False)
    like_status = db.Column(db.SMALLINT, default=0)  # 0 for not liked, 1 for liked, 2 for disliked
    user = db.relationship("Users", back_populates="comments")
    comment = db.relationship("Comments", back_populates="users")

    def __repr__(self):
        return f'user {self.user_id} interacted with comment {self.comment_id}'


class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    fname = db.Column(db.String(20))
    lname = db.Column(db.String(20))
    email = db.Column(db.String(64), unique=True)
    image = db.Column(db.String(64), default='default.jpg')  # might change later
    password = db.Column(db.LargeBinary)
    best_score = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=0)
    courses = db.relationship("UsersCourses", back_populates="user", lazy='dynamic')
    comments = db.relationship("UsersComments", back_populates="user", lazy='dynamic')

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


class Courses(db.Model):
    __tablename__ = 'Courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(500))
    credit_points = db.Column(db.Integer, default=0)
    users = db.relationship("UsersCourses", back_populates="course")
    questions = db.relationship("CoursesQuestions", back_populates="course")
    lecturers = db.relationship("CoursesLecturers", back_populates="course")

    def __repr__(self):
        return f'{self.name}'


class Lecturers(db.Model):
    __tablename__ = 'Lecturers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    sum_ratings = db.Column(db.Integer, default=0)
    num_ratings = db.Column(db.Integer, default=0)
    courses = db.relationship("CoursesLecturers", back_populates="lecturer")

    def __repr__(self):
        return f'{self.name}, average rating: {self.sum_ratings / self.num_ratings}'


class Questions(db.Model):
    __tablename__ = 'Questions'
    id = db.Column(db.Integer, primary_key=True)
    feature = db.Column(db.String(120), nullable=False)
    q_str = db.Column(db.String(200), unique=True, nullable=False)
    courses = db.relationship("CoursesQuestions", back_populates="question")

    def __repr__(self):
        return f'Question #{self.id}: {self.q_str}'


class Comments(db.Model):
    __tablename__ = 'Comments'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('Courses.id'))
    comment = db.Column(db.String(500), nullable=False)
    # likes = db.Column(db.Integer, default=0)
    # dislikes = db.Column(db.Integer, default=0)
    time = db.Column(db.DateTime, default=func.now())
    users = db.relationship("UsersComments", back_populates="comment")

    def __repr__(self):
        return f'{self.comment}'


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
