from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_uploads import IMAGES
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FileField, Label
from wtforms.validators import Length, InputRequired

from app.validators import image_only
from config import Config

ls = Config.SUPPORTED_LANGUAGES
supported_languages = [
    (ls[0], '简体中文(Simplified Chinese)'),
    (ls[1], '繁體中文(Traditional Chinese)'),
    (ls[2], 'English(US)'),
    (ls[3], 'English(GB)')
]

themes = [('/css/bootstrap.min.css', _l(u'Original - Default')),
          ('https://bootswatch.com/3/cerulean/bootstrap.css', 'Cerulean - A calm blue sky'),
          ('https://bootswatch.com/3/cosmo/bootstrap.css', 'Cosmo - An ode to Metro'),
          ('https://bootswatch.com/3/cyborg/bootstrap.css', 'Cyborg - Jet black and electric blue'),
          ('https://bootswatch.com/3/darkly/bootstrap.css', 'Darkly - Flatly in night mode'),
          ('https://bootswatch.com/3/flatly/bootstrap.css', 'Flatly - Flat and modern'),
          ('https://bootswatch.com/3/journal/bootstrap.css', 'Journal - Crisp like a new sheet of paper'),
          ('https://bootswatch.com/3/lumen/bootstrap.css', 'Lumen - Light and shadow'),
          ('https://bootswatch.com/3/paper/bootstrap.css', 'Paper - Material is the metaphor'),
          ('https://bootswatch.com/3/readable/bootstrap.css', 'Readable - Optimized for legibility'),
          ('https://bootswatch.com/3/sandstone/bootstrap.css', 'Sandstone - A touch of warmth'),
          ('https://bootswatch.com/3/simplex/bootstrap.css', 'Simplex - Mini and minimalist'),
          ('https://bootswatch.com/3/slate/bootstrap.css', 'Slate - Shades of gunmetal gray'),
          ('https://bootswatch.com/3/spacelab/bootstrap.css', 'Spacelab - Silvery and sleek'),
          ('https://bootswatch.com/3/superhero/bootstrap.css', 'Superhero - The brave and the blue'),
          ('https://bootswatch.com/3/united/bootstrap.css', 'United - Ubuntu orange and unique font'),
          ('https://bootswatch.com/3/yeti/bootstrap.css', 'Yeti - A friendly foundation')]


class EditProfileForm(FlaskForm):
    # TODO: add placeholder
    avatar = FileField(_l(u'Change avatar'), validators=[image_only], render_kw={
        "accept": ', '.join(['image/' + ext for ext in IMAGES])
    })
    # avatar = FileField(_l(u'Change avatar', validators=[FileAllowed(avatar, _l(u'Images only'))]))
    name = StringField(_l(u'Nickname'), validators=[InputRequired(), Length(0, 64)])
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
