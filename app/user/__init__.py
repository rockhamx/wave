from flask import Blueprint


user = Blueprint('user', __name__)

from .forms import *
from .views import *
