from flask import Flask
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from config import config

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    #    "_ck": "type_ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
# db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
migrate = Migrate()
moment = Moment()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
babel = Babel()
pagedown = PageDown()


def create_app(config_name):
    app = Flask(__name__, static_folder="./static/")
    app.config.from_object(config[config_name])

    db.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    moment.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)
    pagedown.init_app(app)

    from .frontend import frontend
    from .auth import auth
    from .user import user
    from .post import post
    from .api import api
    app.register_blueprint(frontend)
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(api, url_prefix='/api/v0')

    return app
