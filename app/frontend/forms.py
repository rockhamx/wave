from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo, ValidationError


class EditProfileForm(FlaskForm):
    name = StringField('昵称', [Length(0, 64)])
    location = StringField('位置', [Length(0, 64)])
    motto = TextAreaField('个性签名')
    submit = SubmitField('保存')


class PostForm(FlaskForm):
    title = StringField('标题')
    content = TextAreaField('说点什么：')
    is_public = BooleanField('是否公开')
    # tags =
    submit = SubmitField('发布')


