from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_babel import refresh, gettext as _
from flask_login import login_required, current_user

from . import frontend
from app import db, babel
from app.models import User, Post, follows
from .forms import EditProfileForm, PostForm


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


@frontend.route('/home')
@login_required
def home():
    # form = PostForm()
    # if form.validate_on_submit():
    #     pass
    posts = current_user.followed_posts()
    return render_template('user/Followed_posts.html', posts=posts)


# User Profile
@frontend.route('/<username>')
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    posts = u.posts.order_by(Post.edit_timestamp.desc()).all()
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


# @frontend.route('/tags', methods=['GET'])
# @login_required
# def my_tags():
#     tags_id = current_user.tags
#     return render_template('user/tags.html', tags=tags_id)


@frontend.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data,
                    is_public=form.is_public.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_(u'Your post has been published.'))
        return redirect(url_for('.user', username=current_user.username))
    return render_template('user/write.html', form=form)


@frontend.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    form = PostForm()
    post = Post.query.filter_by(id=id).first_or_404()
    if current_user.id != post.author_id:
        flash(_('You have not authorized to this operation.', 'error'))
        return redirect(url_for('.user', username=current_user.username))

    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.is_public = form.is_public.data
        db.session.add(post)
        db.session.commit()
        flash(_(u'You post has been updated.'))
        return redirect(url_for('.user', username=current_user.username))
    form.title.data = post.title
    form.body.data = post.body
    form.is_public.data = post.is_public
    return render_template('user/write.html', form=form)


@frontend.route('/article/<int:id>')
def article(id):
    post = Post.query.filter_by(id=id).first()
    post.click()
    db.session.add(post)
    db.session.commit()
    return render_template('article.html', post=post)


@frontend.route('/newest')
def newest():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.pub_timestamp.desc()).paginate(
        page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
        error_out=False
    ).items
    return render_template('recent.html', posts=posts)


@frontend.route('/follow', methods=['POST'])
@login_required
def follow():
    status = _('Follow')
    u = User.query.filter_by(username=request.form['username']).first()
    if u and current_user != u:
        current_user.follows(u)
        db.session.commit()
        status = _('Following')
    return {'status': status}


@frontend.route('/unfollow', methods=['POST'])
@login_required
def unfollow():
    status = _('Following')
    u = User.query.filter_by(username=request.form['username']).first()
    if u and current_user != u:
        current_user.un_follows(u)
        db.session.commit()
        status = _('Follow')
    return {'status': status}


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
