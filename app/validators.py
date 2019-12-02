from flask_uploads import IMAGES
from flask_babel import lazy_gettext as _l
from wtforms import ValidationError


def image_only(form, field):
    if field.data.filename:
        ext = field.data.filename.split('.')[-1]
        if ext not in IMAGES:
            raise ValidationError(_l(u'Images only'))
