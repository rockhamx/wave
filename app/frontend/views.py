from flask import render_template, request, current_app
from flask_babel import gettext as _
from flask_login import current_user

from . import frontend
from app import babel
from app.models import User, Post, Publication, Tag


# @login_required
@babel.localeselector
def get_locale():
    locale = getattr(current_user, 'locale', None)
    if locale:
        return locale
    return request.accept_languages.best_match(current_app.config['SUPPORTED_LANGUAGES'])


# @login_required
@babel.timezoneselector
def get_timezone():
    if current_user is not None:
        return current_user.timezone


@frontend.route('/index')
@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/about')
def about():
    return render_template('about.html')


@frontend.route('/react')
def react():
    return render_template('react.html')


@frontend.route('/search')
def search():
    query_string = request.args.get('q', default='')
    query = '%{}%'.format(query_string)
    page = request.args.get('page', 1, type=int)
    posts = Post.search(page, query, query, query)
    return render_template('search.html', query=query_string, posts=posts)


@frontend.route('/search/user')
def search_user():
    query_string = request.args.get('q', default='')
    query = '%{}%'.format(query_string)
    page = request.args.get('page', 1, type=int)
    users = User.search(page, query, query)
    return render_template('user/search.html', query=query_string, users=users)


@frontend.route('/search/publication')
def search_pub():
    query_string = request.args.get('q', default='')
    query = '%{}%'.format(query_string)
    page = request.args.get('page', 1, type=int)
    pubs = Publication.search(page, query, query)
    return render_template('publication/search.html', query=query_string, publications=pubs)


@frontend.route('/search/tags')
def search_tag():
    query_string = request.args.get('q', default='')
    query = '%{}%'.format(query_string)
    page = request.args.get('page', 1, type=int)
    tags = Tag.search(page, query, query)
    return render_template('tag/search.html', query=query_string, tags=tags)


# @frontend.route('/tags', methods=['GET'])
# @login_required
# def my_tags():
#     tags_id = current_user.tags
#     return render_template('user/tags.html', tags=tags_id)
