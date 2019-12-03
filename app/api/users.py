from flask import jsonify, url_for
from flask_login import login_required, current_user
from flask_babel import gettext as _

from app import db
from app.models import User, Message
from . import api


@api.route('/follow/<username>', methods=['POST'])
def follow(username):
    result = 'error'
    status = _('Follow')
    next = None
    message = {
        "text": None,
        "type": 'danger'
    }
    # TODO: Use other authentication
    if current_user.is_anonymous:
        next = url_for('auth.login')
        message['text'] = _('Please sign in first.')
        message['type'] = 'info'
    else:
        u = User.query.filter_by(username=username).first()
        if u and current_user != u:
            current_user.follows(u)
            db.session.commit()
            result = 'success'
            status = _('Following')

    return jsonify({
        "result": result,
        "status": status,
        "next": next,
        "message": message
    })


@api.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    status = _('Following')
    u = User.query.filter_by(username=username).first()
    if u and current_user != u:
        current_user.un_follows(u)
        db.session.commit()
        status = _('Follow')

    return jsonify({
        'status': status
    })


@api.route('/unread_messages/count')
@login_required
def count_unread():
    status = 'error'
    count = current_user.unread_messages_count()
    # if count:
    status = 'success'
    return jsonify({
        "status": status,
        "count": count
    })


@api.route('/read/message/<int:id>', methods=['POST'])
@login_required
def read_message(id):
    result, status = 'error', _(u'Unread')
    msg = Message.query.get(int(id))
    if current_user.id == msg.recipient_id:
        if not msg.read:
            msg.read = True
            db.session.add(msg)
            db.session.commit()
        result = 'success'
        status = _(u'Read')
    return jsonify({
        "result": result,
        "status": status
    })