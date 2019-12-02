from flask import render_template, flash, redirect, url_for, request, current_app, abort, jsonify
from flask_babel import gettext as _
from flask_login import login_required, current_user

from . import publication
from app import db
from app.models import Publication


@publication.route('/publication/<name>')
def home(name):
    pub = Publication.query.filter_by(name=name).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = pub.latest(page=page)
    return render_template('publication/home.html', pub=pub, posts=posts)