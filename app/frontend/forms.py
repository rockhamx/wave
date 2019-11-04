from flask_babel import lazy_gettext as _l
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, Length, Regexp, ValidationError


class EditProfileForm(FlaskForm):
    name = StringField(_l(u'Nickname'), [Length(0, 64)])
    location = StringField(_l(u'Location'), [Length(0, 64)])
    description = TextAreaField(_l(u'description'))
    locale = StringField(_l(u'Locale'))
    submit = SubmitField(_l(u'Save profile'))


class PostForm(FlaskForm):
    title = StringField(_l(u'Tittle'), [InputRequired()])
    body = PageDownField(_l(u'Enter your Markdown'), [InputRequired()])
    is_public = BooleanField(_l(u'Only visible for myself'))
    # TODO: add tags field
    # tags =
    submit = SubmitField(_l(u'Publish'))


