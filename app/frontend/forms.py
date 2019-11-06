from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Length


class EditProfileForm(FlaskForm):
    name = StringField(_l(u'Nickname'), [Length(0, 64)])
    location = StringField(_l(u'Location'), [Length(0, 64)])
    description = TextAreaField(_l(u'description'))
    locale = StringField(_l(u'Locale'))
    submit = SubmitField(_l(u'Save profile'))
