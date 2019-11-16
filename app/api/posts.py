from flask_login import login_required, current_user

from app.models import Post, User
from . import api


@api.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get(int(post_id))
    user = User.query.get(current_user.id)
    user.like(post)
    return {'status': 'success'}

