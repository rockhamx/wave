from flask import render_template, flash, redirect, url_for, request, current_app
from flask_babel import refresh, gettext as _
from flask_login import login_required, current_user

from . import frontend
from app import db, babel
from app.models import User, Post
from .forms import EditProfileForm


# @login_required
@babel.localeselector
def get_locale():
    if getattr(current_user, 'locale', None):
        return current_user.locale
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


# User Profile
@frontend.route('/<username>')
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = u.posts.order_by(Post.edit_timestamp.desc()).paginate(
        page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
        error_out=False
    ).items
    return render_template('user/profile.html', user=u, posts=posts)


@frontend.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        old_locale = form.locale.data
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.description = form.description.data
        current_user.locale = form.locale.data
        db.session.add(current_user)
        db.session.commit()
        if current_user.locale != old_locale:
            refresh()
        flash(_(u'Your profile has been updated.'))
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.description.data = current_user.description
    form.locale.data = current_user.locale
    return render_template('user/edit_profile.html', form=form)


@frontend.route('/follow', methods=['POST'])
@login_required
def follow():
    u = User.query.filter_by(username=request.form['username']).first()
    if u and current_user != u and not current_user.is_following(u):
        current_user.follows(u)
        db.session.commit()
        status = _('Following')
        return {'status': status}
    return {}


@frontend.route('/unfollow', methods=['POST'])
@login_required
def unfollow():
    u = User.query.filter_by(username=request.form['username']).first()
    if u and current_user != u and current_user.is_following(u):
        current_user.un_follows(u)
        db.session.commit()
        status = _('Follow')
        return {'status': status}
    return {}


@frontend.route('/<username>/following')
def following(username):
    u = User.query.filter_by(username=username).first_or_404()
    users = u.following_desc_by_time()
    return render_template('user/following.html', username=username, users=users)


@frontend.route('/<username>/followers')
def followers(username):
    u = User.query.filter_by(username=username).first_or_404()
    users = u.followers_desc_by_time()
    return render_template('user/followers.html', username=username, users=users)


# @frontend.route('/tags', methods=['GET'])
# @login_required
# def my_tags():
#     tags_id = current_user.tags
#     return render_template('user/tags.html', tags=tags_id)
