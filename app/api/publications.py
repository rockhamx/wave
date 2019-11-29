from flask import request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Publication
from . import api


@api.route('/publications/', methods=['DELETE'])
@login_required
def delete_pub():
    pass