from flask import render_template
from . import frontend


@frontend.route('/')
def index():
    return render_template('index.html')