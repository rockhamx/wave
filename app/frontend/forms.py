from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import Length, InputRequired


class NewPublicationForm(FlaskForm):
    name = StringField(_l(u'Name'), validators=[InputRequired(), Length(min=0, max=64)],
                       render_kw={"placeholder": _l(u'Publication name, required.')})
    description = TextAreaField(_l(u'Description'),
                                render_kw={"placeholder": _l(u'Description, this is optional.')})
    submit = SubmitField(_l(u'Create'))
