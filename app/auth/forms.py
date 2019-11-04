from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo, ValidationError
from flask_babel import gettext as _
from ..models import User


class RegistrationForm(FlaskForm):
    email = StringField(_(u'Email'), validators=[InputRequired(), Length(1, 64), Email()])
    username = StringField(_(u'Username'), validators=[InputRequired(), Length(1, 64),
                                              Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                     _(u'Username must have only letters, numbers, dots or underscores.'))])  # 用户名只能包括字母，数字，点和下划线
    password = PasswordField(_(u'Password'), validators=[InputRequired(), Length(1, 64)])
    confirmed = PasswordField(_(u'Confirm password'), validators=[InputRequired(), EqualTo('password',
                                                                           _(u'Passwords must match.'))])  # 两次输入的密码必须相同。
    submit = SubmitField(_(u'Register'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError(_(u'Email already registered.')) #邮箱已被注册。

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError(_(u'Username already in use.'))  #用户名已被使用。


class LoginForm(FlaskForm):
    email = StringField(_(u'Email'), validators=[InputRequired(), Length(1, 64)])
    password = PasswordField(_(u'Password'), validators=[InputRequired(), Length(1, 64)])
    remember = BooleanField(_(u'Keep me logged in'))
    submit = SubmitField(_(u'Log In'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(_(u'Old password'), validators=[InputRequired()])
    password = PasswordField(_(u'New password'), validators=[
        InputRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField(_(u'Confirm new password'),
                              validators=[InputRequired()])
    submit = SubmitField(_(u'Update Password'))


class ChangeEmailForm(FlaskForm):
    email = StringField(_(u'New Email'), validators=[InputRequired(), Length(1, 64),
                                              Email()])
    password = PasswordField(_(u'Password'), validators=[InputRequired()])
    submit = SubmitField(_(u'Update Email Address'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError(_(u'Email already registered.'))
        if self.email == field.data.lower():
            raise ValidationError(_(u'Your are using the old email address.'))  # 您输入的电子邮箱与之前的相同。


class PasswordResetRequestForm(FlaskForm):
    email = StringField(_(u'Email'), validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField(_(u'Reset Password'))  # 发送重置密码邮件


class PasswordResetForm(FlaskForm):
    password = PasswordField(_(u'New Email'), validators=[
        InputRequired(), EqualTo('password2', message='Passwords must match')])  # 两次输入的密码必须相同。
    password2 = PasswordField(_(u'Confirm password'), validators=[InputRequired()])  # 再次输入新密码
    submit = SubmitField(_(u'Reset Password'))  # 重置密码

