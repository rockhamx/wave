from flask import render_template, flash, redirect, url_for, request, current_app, abort, jsonify
from flask_babel import gettext as _
from flask_login import login_required, current_user

from . import post
from app import db
from app.models import Post
from .forms import PostForm


@post.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    form = PostForm()
    if form.validate_on_submit():
        p = Post(title=form.title.data, body=form.body.data,
                 is_public=form.is_public.data, author=current_user)
        db.session.add(p)
        db.session.commit()
        flash(_(u'Your post has been published.'))
        return redirect(url_for('frontend.user', username=current_user.username))
    return render_template('user/write.html', form=form)


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
    id = request.form['id']
    if id:
        p = Post.query.filter_by(id=id).first()
        if p:
            db.session.delete(p)
            db.session.commit()
            result = "Success"
    return jsonify({
        "status": result
    })


@post.route('/article/<int:id>')
def article(id):
    p = Post.query.filter_by(id=id).first()
    p.click()
    db.session.add(p)
    db.session.commit()
    return render_template('article.html', post=p)


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