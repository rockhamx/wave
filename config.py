import os
from dotenv import load_dotenv


base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    # website global
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SERVER_NAME = os.environ.get('SERVER_NAME')
    # WAVE_APP_FOLDER = ''
    WAVE_INSTANCE_FOLDER = 'instance'
    WAVE_POSTS_PER_PAGE = 10
    WAVE_AVATAR_REQUIRED_SIZE = [30, 42, 60, 80, 100, 256]
    WAVE_ALLOWED_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'p', 'a', 'img',
                         'ol', 'ul', 'li', 'pre', 'code', 'blockquote',
                         'i', 'abbr', 'acronym', 'b', 'strong', 'em', 'u']
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///' + os.path.join(base_dir, 'data-dev.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') or False
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_SUFFIX = os.environ.get('MAIL_SUFFIX') or ''
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # flask_babel
    SUPPORTED_LANGUAGES = ['zh_CN', 'zh_TW', 'en_US', 'en_GB']
    BABEL_DEFAULT_LOCALE = SUPPORTED_LANGUAGES[0]
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    # Flask Uploads
    # UPLOADS_DEFAULT_DEST =
    # Flask Admin
    FLASK_ADMIN_SWATCH = 'paper'
    # the following comment will be deprecated due to the insecurity
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
