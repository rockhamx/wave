from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo, ValidationError
from flask_babel import lazy_gettext as _l
from ..models import User


class RegistrationForm(FlaskForm):
    email = StringField(_l(u'Email'), validators=[InputRequired(), Length(1, 64), Email()])
    username = StringField(_l(u'Username'),
                           validators=[InputRequired(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              _l(u'Username must have only letters, numbers, dots or underscores.'))])
    password = PasswordField(_l(u'Password'), validators=[InputRequired(), Length(1, 64)])
    confirmed = PasswordField(_l(u'Confirm password'),
                              validators=[InputRequired(), EqualTo('password', _l(u'Passwords must match.'))])
    submit = SubmitField(_l(u'Register'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError(_l(u'Email already registered.'))  # 邮箱已被注册。

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError(_l(u'Username already in use.'))  # 用户名已被使用。


class LoginForm(FlaskForm):
    email = StringField(_l(u'Email'), validators=[InputRequired(), Length(1, 64)])
    password = PasswordField(_l(u'Password'), validators=[InputRequired(), Length(1, 64)])
    remember = BooleanField(_l(u'Keep me logged in'))
    submit = SubmitField(_l(u'Log In'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(_l(u'Old password'), validators=[InputRequired()])
    password = PasswordField(_l(u'New password'), validators=[
        InputRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField(_l(u'Confirm new password'),
                              validators=[InputRequired()])
    submit = SubmitField(_l(u'Update Password'))


class ChangeEmailForm(FlaskForm):
    email = StringField(_l(u'New Email'), validators=[InputRequired(), Length(1, 64),
                                                      Email()])
    password = PasswordField(_l(u'Password'), validators=[InputRequired()])
    submit = SubmitField(_l(u'Update Email Address'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError(_l(u'Email already registered.'))
        if self.email == field.data.lower():
            raise ValidationError(_l(u'Your are using the old email address.'))  # 您输入的电子邮箱与之前的相同。


class PasswordResetRequestForm(FlaskForm):
    email = StringField(_l(u'Email'), validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField(_l(u'Reset Password'))  # 发送重置密码邮件


class PasswordResetForm(FlaskForm):
    password = PasswordField(_l(u'New Email'), validators=[
        InputRequired(), EqualTo('password2', message='Passwords must match')])  # 两次输入的密码必须相同。
    password2 = PasswordField(_l(u'Confirm password'), validators=[InputRequired()])  # 再次输入新密码
    submit = SubmitField(_l(u'Reset Password'))  # 重置密码
