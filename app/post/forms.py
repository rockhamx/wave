from flask_babel import lazy_gettext as _l
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import InputRequired


class PostForm(FlaskForm):
    title = StringField(_l(u'Tittle'), [InputRequired()])
    body = PageDownField(_l(u'Enter your Markdown'), [InputRequired()])
    is_public = BooleanField(_l(u'Only visible for myself'))
    # TODO: add tags field
    # tags =
    submit = SubmitField(_l(u'Publish'))


