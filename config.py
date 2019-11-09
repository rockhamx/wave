import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    # website global
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'M\xf7CX\x16$\xb7-\x1bi\xe9\x86T\xebm\xda'
    SERVER_NAME = os.environ.get('SERVER_NAME')
    WAVE_POSTS_PER_PAGE = 20
    WAVE_ALLOWED_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a',
                    'ol', 'ul', 'li', 'pre', 'code', 'blockquote',
                    'i',  'abbr', 'acronym', 'b', 'strong', 'em']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 465
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') or False
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_SUFFIX = os.environ.get('MAIL_SUFFIX') or ''
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # flask_babel
    SUPPORTED_LANGUAGES = ['en', 'zh_CN']
    BABEL_DEFAULT_LOCALE = SUPPORTED_LANGUAGES[1]
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    # the following comment will be deprecated due to the insecurity
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///' + os.path.join(base_dir, 'data-dev.sqlite')


class TestingConfig(Config):
    Testing = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
