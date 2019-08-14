from . import frontend
from flask import render_template


@frontend.route('/')
def index():
    return render_template('index.html')