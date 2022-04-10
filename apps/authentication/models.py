# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass


class UsersCourses(db.Model):
    __tablename__ = 'UsersCourses'
    user_id = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    course_id = db.Column(db.ForeignKey('Courses.id'), primary_key=True)
    status = db.Column(db.SMALLINT)  # 0 for taking rn, 1 for finished & unanswered, 2 for answered
    user = db.relationship("Users", back_populates="courses")
    course = db.relationship("Courses", back_populates="users")

    def __repr__(self):
        status_repr = ['is taking', 'has finished & did not rate', 'has finished and rated']
        return f'user {self.user_id} {status_repr[self.status]} course {self.course_id}'


class CoursesQuestions(db.Model):
    __tablename__ = 'CoursesQuestions'
    course_id = db.Column(db.ForeignKey('Courses.id'), primary_key=True)
    question_id = db.Column(db.ForeignKey('Questions.id'), primary_key=True)
    avg_rating = db.Column(db.Integer, default=0)
    ans_count = db.Column(db.Integer, default=0)
    course = db.relationship("Courses", back_populates="questions")
    question = db.relationship("Courses", back_populates="users")

    def __repr__(self):
        status_repr = ['is taking', 'has finished & did not rate', 'has finished and rated']
        return f'user {self.user_id} {status_repr[self.status]} course {self.course_id}'


class Users(db.Model, UserMixin):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    fname = db.Column(db.String(20))
    lname = db.Column(db.String(20))
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    best_score = db.Column(db.Integer, default=0)
    courses = db.relationship("UsersCourses", back_populates="user")

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
    currLecturer = db.Column(db.String(26))
    users = db.relationship("UsersCourses", back_populates="course")
    questions = db.relationship("CoursesQuestions", back_populates="course")

    def __repr__(self):
        return f'{self.name} by {self.currLecturer}'


class Questions(db.Model):
    __tablename__ = 'Questions'
    id = db.Column(db.Integer, primary_key=True)
    q_str = db.Column(db.String(200), unique=True, nullable=False)
    courses = db.relationship("CoursesQuestions", back_populates="question")

    def __repr__(self):
        return f'Question #{self.id}: {self.q_str}'


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None


if __name__ == '__main__':
    algo = Courses(id=0, name="Algorithms", currLecturer="Rani Hod")
    print(algo)
