from flask import render_template, flash, redirect, url_for, request, current_app, abort, jsonify
from flask_babel import gettext as _
from flask_login import login_required, current_user

from . import post
from app import db
from app.models import Post, Draft, Tag, Comment, Publication
from .forms import PostEditorForm, CommentForm, RichTextEditorForm


@post.route('/articles')
# @post.route('/articles/draft')
# @post.route('/articles/published')
@login_required
def articles():
    # user = current_user._get_current_object()
    page = request.args.get('page', 1, type=int)
    drafts = current_user.drafts_desc_by_time(page=page)
    posts = current_user.latest_posts(page=page)
    return render_template('user/articles.html', drafts=drafts, posts=posts)


@post.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    form = PostEditorForm()
    if form.validate_on_submit():
        p = Post(title=form.title.data, body=form.body.data,
                 is_public=form.is_public.data, author=current_user._get_current_object())
        db.session.add(p)
        db.session.commit()
        flash(_(u'Your post has been published.'))
        return redirect(url_for('user.profile', username=current_user.username))
    return render_template('user/write.html', form=form)


@post.route('/p/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    p = Post.query.filter_by(id=id, author_id=current_user.id).first_or_404()

    if not p.body:
        draf = Draft.query.filter_by(reference_id=p.id).first()
        if draf:
            return redirect(url_for('post.draft', id=draf.id))
        form = RichTextEditorForm()
        form.reference_id.data = p.id
        form.title.data = p.title
        form.subtitle.data = p.subtitle
        form.description.data = p.description
        form.content.data = p.html
        form.publication.choices.extend([(pub.id, pub.name) for pub in current_user.followed_pubs_desc_by_time()])
        form.publication.data = p.publication.id if p.publication else ''
        form.tags.data = ' '.join([str(tag) for tag in p.tags])
        form.private.data = not p.is_public
        return render_template('new.html', form=form)

    form = PostEditorForm()
    if form.validate_on_submit():
        p.title = form.title.data
        p.body = form.body.data
        p.is_public = not form.is_public.data
        db.session.add(p)
        db.session.commit()
        flash(_(u'Your post has been updated.'))
        return redirect(url_for('frontend.user', username=current_user.username))
    form.title.data = p.title
    form.body.data = p.body
    form.private.data = not p.is_public
    return render_template('user/write.html', form=form)


@post.route('/new')
@login_required
def new():
    form = RichTextEditorForm()
    form.publication.choices.extend([(pub.id, pub.name) for pub in current_user.followed_pubs_desc_by_time()])
    return render_template('new.html', form=form)


@post.route('/d/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def draft(id):
    d = Draft.query.filter_by(id=id, author_id=current_user.id).first_or_404()
    form = RichTextEditorForm()
    form.publication.choices.extend([(pub.id, pub.name) for pub in current_user.followed_pubs_desc_by_time()])

    if form.validate_on_submit():
        if form.reference_id.data:
            p = Post.query.filter_by(id=form.reference_id.data, author_id=current_user.id).first_or_404()
        else:
            p = Post()
            p.author = current_user._get_current_object()

        tags = []
        if form.tags.data:
            for tag in form.tags.data.split():
                tag = Tag.get_or_create(tag.strip())
                if tag and tag not in p.tags:
                    tags.append(tag)
        publication = Publication.query.get(form.publication.data)
        p.update(title=form.title.data, subtitle=form.subtitle.data, description=form.description.data,
                 html=form.content.data, is_public=not form.private.data, publication=publication, tags=tags)

        db.session.add(p)
        db.session.delete(d)
        db.session.commit()
        flash(_(u'Your post has been updated.'))
        return redirect(url_for('post.article', id=p.id))

    # form = RichTextEditorForm(id=id, reference_id=d.reference_id, type=d.type, title=d.title, subtitle=d.title,
    #                           description=d.description, content=d.content, tags=d.tags, private=not d.is_public)
    form.id.data = d.id
    form.reference_id.data = d.reference_id
    form.type.data = d.type
    form.title.data = d.title
    form.subtitle.data = d.subtitle
    form.description.data = d.description
    form.content.data = d.content
    form.publication.data = d.publication.id if d.publication else ''
    form.tags.data = d.tags
    form.private.data = not d.is_public
    return render_template('new.html', form=form)


@post.route('/newest')
def newest():
    page = request.args.get('page', 1, type=int)
    posts = Post.newest(page)
    return render_template('newest.html', posts=posts)


@post.route('/article/<int:id>', methods=['GET', 'POST'])
def article(id):
    form = CommentForm()
    post = Post.query.filter_by(id=id).first_or_404()
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

# @post.route('/delete_post', methods=['POST'])
# @login_required
# def delete():
#     result = "error"
#     id = request.form.get('id', None)
#     if id:
#         p = Post.query.filter_by(id=id).first()
#         if p:
#             db.session.delete(p)
#             db.session.commit()
#             result = "success"
#     return jsonify({
#         "status": result
#     })
