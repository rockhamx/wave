from flask import Blueprint


auth = Blueprint('auth', __name__)

from .forms import *
from .views import *