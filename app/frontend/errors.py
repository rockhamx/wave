from flask import render_template
from . import frontend


@frontend.app_errorhandler(404)
def not_found():
    return render_template('/errors/404.html'), 404

@frontend.app_errorhandler(500)
def internal_server_error():
    return render_template('/errors/500.html'), 500