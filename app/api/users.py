from flask import jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Message
from . import api


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
    status = 'error'
    msg = Message.query.get(int(id))
    if current_user.id == msg.recipient_id:
        if not msg.read:
            msg.read = True
            db.session.add(msg)
            db.session.commit()
        status = 'success'
    return jsonify({
        "status": status
    })