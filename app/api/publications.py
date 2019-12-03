from flask import jsonify, url_for
from flask_login import login_required, current_user
from flask_babelex import gettext as _

from app import db
from app.models import Publication, User
from . import api


@api.route('/publications/', methods=['DELETE'])
@login_required
def delete_pub():
    pass


@api.route('/follow/publication/<int:id>', methods=['POST'])
def follow_pub(id):
    result = 'error'
    status = _('Follow')
    next = None
    message = {
        "text": None,
        "type": None,
    }
    # TODO: Use other authentication
    if current_user.is_anonymous:
        next = url_for('auth.login')
        message['text'] = _('Please sign in first.')
        message['type'] = 'info'
    else:
        pub = Publication.query.get(int(id))
        if pub:
            user = User.query.get(current_user.id)
            user.follow_publication(pub)
            db.session.commit()
            result = 'success'
            status = _('Following')
    return jsonify({
        "result": result,
        "status": status,
        "next": next,
        "message": message
    })


@api.route('/unfollow/publication/<int:id>', methods=['POST'])
@login_required
def unfollow_pub(id):
    status = _('Following')
    pub = Publication.query.get(int(id))
    if pub:
        user = User.query.get(current_user.id)
        user.unfollow_publication(pub)
        db.session.commit()
        status = _('Follow')
    return jsonify({
        "result": "success",
        "status": status
    })

