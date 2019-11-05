import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = b'M\xf7CX\x16$\xb7-\x1bi\xe9\x86T\xebm\xda'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    WAVE_MAIL_SENDER = 'Wave <rockhamx@gmail.com>'
    WAVE_MAIL_SUFFIX = 'Wave'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # flask_babel
    SUPPORTED_LANGUAGES = ['en', 'zh_CN']
    BABEL_DEFAULT_LOCALE = SUPPORTED_LANGUAGES[1]
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    # website global
    ALLOWED_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a',
                    'ol', 'ul', 'li', 'pre', 'code', 'blockquote',
                    'i',  'abbr', 'acronym', 'b', 'strong', 'em']

    # the following comment will be deprecated due to the insecurity
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///' + os.path.join(base_dir, 'data-dev.sqlite')


class TestingConfig(Config):
    Testing = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///' + os.path.join(base_dir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///' + os.path.join(base_dir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
