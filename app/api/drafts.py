from flask import request, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _

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
            "result": "error"
        })


@api.route('/drafts/', methods=['POST'])
@login_required
def save_draft():
    result, status = 'error', ''
    d = Draft.from_json(request.json)
    if d:
        if d.id:
            d.update_from_json(request.json)
        else:
            d.author_id = current_user.id
        db.session.add(d)
        db.session.commit()
        result = 'success'
        status = _(u'Saved')

    return jsonify({
        "result": result,
        "status": status,
        "id": d.id,
    })


@api.route('/draft/<int:id>', methods=['DELETE'])
@login_required
def delete_draft(id):
    result = 'error'
    if id:
        d = Draft.query.filter_by(id=id).first()
        if d:
            db.session.delete(d)
            db.session.commit()
            result = "success"
    return jsonify({
        "result": result,
    })
