from flask import Blueprint


frontend = Blueprint('frontend', __name__)
#, '../templates'

from . import views