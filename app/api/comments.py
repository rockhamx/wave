from flask import request, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _

from app import db
from app.models import Comment
from . import api


@api.route('/comment/<int:id>', methods=['DELETE'])
def delete_comment(id):
    result = 'failed'
    if id:
        c = Comment.query.get(int(id))
        if c:
            db.session.delete(c)
            db.session.commit()
            status = "success"
            # next_url = url_for('user.profile', username=current_user.username)
            result = 'success'
    return jsonify({
        "result": result
    })