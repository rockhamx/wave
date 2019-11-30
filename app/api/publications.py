from flask import request, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _

from app import db
from app.models import Publication, User
from . import api


@api.route('/publications/', methods=['DELETE'])
@login_required
def delete_pub():
    pass


@api.route('/follow/publication/<int:id>', methods=['POST'])
@login_required
def follow_pub(id):
    status = _('Follow')
    pub = Publication.query.get(int(id))
    if pub:
        user = User.query.get(current_user.id)
        user.follow_publication(pub)
        db.session.commit()
        status = _('Following')
    return jsonify({
        "result": "success",
        "status": status
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

