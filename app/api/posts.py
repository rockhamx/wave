from flask_login import login_required, current_user

from app.models import Post, User
from . import api


@api.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    status = 'error'
    post = Post.query.get(int(post_id))
    if post:
        user = User.query.get(current_user.id)
        user.like(post)
        status = 'success'
    return {'status': status}


@api.route('bookmarks/<int:post_id>', methods=['POST'])
@login_required
def bookmarks(post_id):
    status = 'error'
    post = Post.query.get(int(post_id))
    if post:
        user = User.query.get(current_user.id)
        user.add_bookmark(post)
        status = 'success'
    return {'status': status}