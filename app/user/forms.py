import json
import os

from flask_babel import lazy_gettext as _l
from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Length, InputRequired

from config import Config

images = UploadSet('images', IMAGES)
ls = Config.SUPPORTED_LANGUAGES
supported_languages = [
    (ls[0], '简体中文(Simplified Chinese)'),
    (ls[1], '繁體中文(Traditional Chinese)'),
    (ls[2], 'English(US)'),
    (ls[3], 'English(GB)')
]

# themes
themes = [
    ('/css/bootstrap.min.css', _l(u'Original - Default')),
]
with open(os.path.join('instance', 'bootswatch.json'), 'r') as fp:
    bootswatch = json.load(fp)
    for index, theme in enumerate(bootswatch['themes'], start=1):
        themes.append((theme['css'], '{} - {}'.format(theme['name'], theme['description'])))


class EditProfileForm(FlaskForm):
    # TODO: add placeholder
    avatar = FileField(_l(u'Change avatar', validators=[FileRequired(), FileAllowed(images, _l(u'Images only'))]))
    name = StringField(_l(u'Nickname'), validators=[Length(0, 64)])
    location = StringField(_l(u'Location'), validators=[Length(0, 64)])
    description = TextAreaField(_l(u'description'))
    # locale = SelectField(_l(u'Locale'), choices=supported_languages)
    submit = SubmitField(_l(u'Save profile'))


class MessageForm(FlaskForm):
    message = TextAreaField(_l(u'Message'),
                            validators=[InputRequired(), Length(min=1, max=256)],
                            render_kw={"placeholder": _l(u'What would you like to say?')})
    submit = SubmitField(_l(u'Send'))


class PreferenceForm(FlaskForm):
    # timezone =
    locale = SelectField(_l(u'Language'), choices=supported_languages)
    theme = SelectField(_l(u'Theme'), choices=themes)
    submit = SubmitField(_l(u'Save preference'))
