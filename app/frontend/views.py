from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import frontend
from app import db
from app.models import User, Post, Users_Tags
from .forms import EditProfileForm, PostForm


@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/home')
@login_required
def home():
    form = PostForm()
    if form.validate_on_submit():
        pass
    posts = current_user.posts.order_by(Post.edit_timestamp.desc()).all()
    return render_template('home.html', form=form, posts=posts)


@frontend.route('/user/<username>')
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    return render_template('user/profile.html', user=u)


@frontend.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.motto = form.motto.data
        db.session.add(current_user)
        db.session.commit()
        flash('您的个人信息已更新。')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.motto.data = current_user.motto
    return render_template('user/edit_profile.html', form=form)


# @frontend.route('/tags', methods=['GET'])
# @login_required
# def my_tags():
#     tags_id = current_user.tags
#     return render_template('user/tags.html', tags=tags_id)


@frontend.route('/posts')
@login_required
def my_posts():
    posts = current_user.posts
    return render_template('user/posts.html', posts=posts)


@frontend.route('/follows')
@login_required
def follows():
    posts = Post.query.filter_by(author_id=current_user.id).order_by(Post.pub_timestamp.desc()).all()
    return render_template('user/posts.html', posts=posts)


@frontend.route('/followed')
@login_required
def followed():
    posts = Post.query.filter_by(author_id=current_user.id).order_by(Post.pub_timestamp.desc()).all()
    return render_template('user/posts.html', posts=posts)
