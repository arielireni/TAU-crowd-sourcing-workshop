from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired


# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                           id='username_login',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()])
    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
    fname = StringField('First Name',
                        id='fname_create',
                        validators=[DataRequired()])
    lname = StringField('Last Name',
                        id='lname_create',
                        validators=[DataRequired()])
    image = StringField('Image',
                        id='img_create',
                        validators=[DataRequired()])
