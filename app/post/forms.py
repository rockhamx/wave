from flask_babel import lazy_gettext as _l
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, HiddenField, SelectField, Label
from wtforms.validators import InputRequired


class PostEditorForm(FlaskForm):
    title = StringField(_l(u'Tittle'), [InputRequired()])
    body = PageDownField(_l(u'Enter your Markdown'), [InputRequired()])
    is_public = BooleanField(_l(u'Only visible for myself'))
    # TODO: add tags field
    # tags =
    submit = SubmitField(_l(u'Publish now'))


class RichTextEditorForm(FlaskForm):
    id = HiddenField()
    reference_id = HiddenField()
    type = HiddenField(default='richText')
    content = HiddenField('')
    title = StringField(_l(u'Tittle'), [InputRequired()],
                        render_kw={'placeholder': _l(u'Required.')})
    subtitle = StringField(_l(u'Subtitle'),
                           render_kw={'placeholder': _l(u'Optional.')})
    description = TextAreaField(_l(u'Description'),
                                render_kw={'placeholder': _l(u'Optional.')})
    # note = Label('', _l('Note: Changes here will affect how your article appears in public places like Wave’s homepage'
    #                     ' — not the article itself.'))
    publication = SelectField(_l('Publish on publication'), coerce=int, choices=[(-1, '')])
    tags = StringField(_l(u'Add or change tags (separate by space) so readers know what your article is about.'),
                       render_kw={'placeholder': _l(u'Add a tag...')})
    private = BooleanField(_l(u'Only visible for myself'))
    submit = SubmitField(_l(u'Publish now'))

    # def __call__(self, id=None, reference_id=None, type=None, content=None, title=None, subtitle=None, description=None,
    #              publication=None, tags=None, private=None):
    #     if id:
    #         self.id.data = id
    #     if reference_id:
    #         self.reference_id =


class CommentForm(FlaskForm):
    content = TextAreaField(_l(u'What\'s in your mind?'), [InputRequired()])
    submit = SubmitField(_l(u'Publish'))
