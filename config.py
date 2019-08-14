import os

class Config:
    SECRET_KEY = os.getenv('PATH') or 'secret string'


class DevelopmentConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    Testing = True


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
