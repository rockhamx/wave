from flask import Blueprint


surfer = Blueprint('surfer', __name__)

from .forms import *
from .views import *