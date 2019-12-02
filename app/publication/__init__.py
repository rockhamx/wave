from flask import Blueprint


publication = Blueprint('publication', __name__)

from . import views