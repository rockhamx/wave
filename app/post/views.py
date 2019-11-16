from flask import render_template, flash, redirect, url_for, request, current_app, abort, jsonify
from flask_babel import gettext as _
from flask_login import login_required, current_user

from . import post
from app import db
from app.models import Post, Comment
from .forms import PostForm, CommentForm


@post.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    form = PostForm()
    if form.validate_on_submit():
        p = Post(title=form.title.data, body=form.body.data,
                 is_public=form.is_public.data, author=current_user._get_current_object())
        db.session.add(p)
        db.session.commit()
        flash(_(u'Your post has been published.'))
        return redirect(url_for('frontend.user', username=current_user.username))
    return render_template('user/write.html', form=form)


@post.route('/new')
@login_required
def new():
    return render_template('new.html')


@post.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    form = PostForm()
    p = Post.query.filter_by(id=id).first_or_404()
    if current_user.id != p.author_id:
        flash(_('You have not authorized to this operation.', 'error'))
        return redirect(url_for('.user', username=current_user.username))

    if form.validate_on_submit():
        p.title = form.title.data
        p.body = form.body.data
        p.is_public = form.is_public.data
        db.session.add(p)
        db.session.commit()
        flash(_(u'You post has been updated.'))
        return redirect(url_for('frontend.user', username=current_user.username))
    form.title.data = p.title
    form.body.data = p.body
    form.is_public.data = p.is_public
    return render_template('user/write.html', form=form)


@post.route('/delete_post', methods=['POST'])
@login_required
def delete():
    result = "Failure"
    id = request.form.get('id', None)
    if id:
        p = Post.query.filter_by(id=id).first()
        if p:
            db.session.delete(p)
            db.session.commit()
            result = "Success"
    return jsonify({
        "status": result
    })


@post.route('/newest')
def newest():
    page = request.args.get('page', 1, type=int)
    posts = Post.newest(page)
    return render_template('newest.html', posts=posts)


@post.route('/followed')
@login_required
def followed():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts(page)
    return render_template('Followed_posts.html', posts=posts)


@post.route('/search')
def search():
    query = request.args.get('q', default='')
    query = '%{}%'.format(query)
    page = request.args.get('page', 1, type=int)
    posts = Post.search(page, query, query, query)
    return render_template('search.html', posts=posts)


@post.route('/article/<int:id>', methods=['GET', 'POST'])
def article(id):
    form = CommentForm()
    post = Post.query.filter_by(id=id).first()
    comments = post.comments_desc_by_time()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            redirect(url_for('frontend.login'))
        comment = Comment(content=form.content.data,
                          author_id=current_user.id,
                          post_id=id)
        db.session.add(comment)
        db.session.commit()
        flash(_(u'Your comment has been published.'))
        return redirect(url_for('post.article', id=id))
    return render_template('article.html', post=post, comments=comments, form=form)


# @post.route('/')