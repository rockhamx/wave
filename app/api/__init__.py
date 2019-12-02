from flask import Blueprint

api = Blueprint('api', __name__)

from . import posts, drafts, users, comments, publications
