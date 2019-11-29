from flask import request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Draft
from . import api


@api.route('/draft/<int:id>', methods=['GET'])
@login_required
def draft(id):
    draft = Draft.query.get(id)
    if draft:
        return draft.to_json()
    else:
        return jsonify({
            "status": "error"
        })


@api.route('/drafts/', methods=['POST'])
@login_required
def save_draft():
    status = "error"
    draft = Draft.from_json(request.json)
    if draft:
        if draft.id:
            draft.update_from_json(request.json)
        else:
            draft.author_id = current_user.id
        db.session.add(draft)
        db.session.commit()
        status = 'success'

    return jsonify({
        "status": status,
        "id": draft.id,
    })


@api.route('/draft/<int:id>', methods=['DELETE'])
@login_required
def delete_draft(id):
    status = "error"
    if id:
        d = Draft.query.filter_by(id=id).first()
        if d:
            db.session.delete(d)
            db.session.commit()
            status = "success"
    return jsonify({
        "status": status
    })
