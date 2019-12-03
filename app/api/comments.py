from flask import jsonify
from flask_babelex import gettext as _

from app import db
from app.models import Comment
from . import api


@api.route('/comment/<int:id>', methods=['DELETE'])
def delete_comment(id):
    result = 'error'
    message = {
        "text": _('Internal Error.'),
        "type": 'danger'
    }
    if id:
        c = Comment.query.get(int(id))
        if c:
            db.session.delete(c)
            db.session.commit()
            # next_url = url_for('user.profile', username=current_user.username)
            result = 'success'
            message['text'] = _(u'Delete success.')
            message['type'] = result

    return jsonify({
        "result": result,
        "message": message
    })
