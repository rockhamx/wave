from flask import request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Post, User, Tag
from . import api


@api.route('/post/<int:id>/edit', methods=['GET'])
@login_required
def edit_post(id):
    pass


@api.route('/posts/', methods=['POST'])
@login_required
def post():
    # status = 'failed'
    post = Post.from_json(request.json, type='html')
    post.author = current_user._get_current_object()
    tags = request.json.get("tags", None)
    if tags:
        for tag in tags.split(','):
            tag = Tag.get_or_create(tag)
            post.tags.append(tag)
    db.session.add(post)
    db.session.commit()
    status = 'success'
    return jsonify({
        "status": status,
        "id": post.id
    })


@api.route('/post/<int:id>', methods=['DELETE'])
@login_required
def delete_post(id):
    status = "error"
    if id:
        p = Post.query.filter_by(id=id).first()
        if p:
            db.session.delete(p)
            db.session.commit()
            status = "success"
    return jsonify({
        "status": status
    })


@api.route('/hearts/<int:id>', methods=['GET'])
@login_required
def hearts_amount(id):
    status = 'error'
    post = Post.query.get(int(id))
    amount = None
    if post:
        amount = current_user.hearts_amount(post)
        status = 'success'
    return jsonify({
        "status": status,
        "amount": amount
    })


@api.route('/hearts/<int:id>', methods=['POST'])
@login_required
def hearts(id):
    status = 'error'
    post = Post.query.get(int(id))
    if post:
        amount = request.json.get('amount', 1)
        user = User.query.get(current_user.id)
        user.like(post, amount=amount)
        db.session.add(user)
        db.session.commit()
        status = 'success'
    return jsonify({'status': status})


@api.route('/hearts/<int:id>', methods=['DELETE'])
@login_required
def un_hearts(id):
    status = 'error'
    post = Post.query.get(int(id))
    if post:
        user = User.query.get(current_user.id)
        user.unlike(post)
        db.session.add(user)
        db.session.commit()
        status = 'success'
    return jsonify({'status': status})


@api.route('/bookmarks/<int:id>', methods=['POST'])
@login_required
def add_bookmark(id):
    status = 'error'
    post = Post.query.get(int(id))
    if post:
        user = User.query.get(current_user.id)
        user.add_bookmark(post)
        db.session.commit()
        status = 'success'
    return jsonify({
        'status': status
    })


@api.route('/bookmarks/<int:id>', methods=['DELETE'])
@login_required
def remove_bookmark(id):
    status = 'error'
    post = Post.query.get(int(id))
    if post:
        user = User.query.get(current_user.id)
        if user.remove_bookmark(post):
            db.session.commit()
            status = 'success'
    return {'status': status}
