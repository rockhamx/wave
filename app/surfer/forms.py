from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[InputRequired(), Length(1,64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                   'Username must have only letters, numbers, dots or underscores.')])
    password = PasswordField('Password', validators=[InputRequired(), Length(1, 64)])
    confirmed = PasswordField('Confirm password', validators=[InputRequired(), EqualTo('password',
                                                                                       'Passwords must match.')])
    submit = SubmitField('Register')




class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(1,64)])
    password = PasswordField('Password', validators=[InputRequired(), Length(1, 64)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')