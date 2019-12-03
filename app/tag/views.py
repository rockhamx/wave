from flask import render_template, request
from flask_babelex import gettext as _

from . import tag
from app import db
from app.models import Tag


@tag.route('/tag/<name>')
def home(name):
    t = Tag.query.filter_by(name=name).first_or_404()
    page = request.args.get('page', 1, type=int)
    # posts = pub.latest(page=page)
    return render_template('tag/home.html', tag=t)