from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo, ValidationError
from ..models import User


class RegistrationForm(FlaskForm):
    email = StringField('电子邮箱', validators=[InputRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[InputRequired(), Length(1, 64),
                                              Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                     '用户名只能包括字母，数字，点和下划线')])  # Username must have only letters, numbers, dots or underscores.
    password = PasswordField('密码', validators=[InputRequired(), Length(1, 64)])
    confirmed = PasswordField('验证密码', validators=[InputRequired(), EqualTo('password',
                                                                           '两次输入的密码必须相同。')])  # Passwords must match.
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('邮箱已被注册。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('用户名已被使用。')


class LoginForm(FlaskForm):
    email = StringField('电子邮箱', validators=[InputRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[InputRequired(), Length(1, 64)])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[InputRequired()])
    password = PasswordField('新密码', validators=[
        InputRequired(), EqualTo('password2', message='两次输入的密码必须相同。')])
    password2 = PasswordField('再次输入新密码',
                              validators=[InputRequired()])
    submit = SubmitField('更新密码')


class ChangeEmailForm(FlaskForm):
    email = StringField('新的电子邮箱', validators=[InputRequired(), Length(1, 64),
                                              Email()])
    password = PasswordField('密码', validators=[InputRequired()])
    submit = SubmitField('更新电子邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该电子邮箱已被注册。')
        if self.email == field.data.lower():
            raise ValidationError('您输入的电子邮箱与之前的相同。')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('您的电子邮箱', validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField('发送重置密码邮件')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        InputRequired(), EqualTo('password2', message='两次输入的密码必须相同。')])
    password2 = PasswordField('再次输入新密码', validators=[InputRequired()])
    submit = SubmitField('重置密码')

