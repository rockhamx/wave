from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_babel import Babel
from flask_mail import Mail
from flask_moment import Moment
from flask_admin import Admin
from flask_pagedown import PageDown
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
admin = Admin(name='wave', template_mode='bootstrap3')
pagedown = PageDown()


def create_app(config_name):
    app = Flask(__name__, static_folder="./static/")
    app.config.from_object(config[config_name])

    db.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db, render_as_batch=(True if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI'] else False))
    moment.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)
    admin.init_app(app)
    pagedown.init_app(app)

    # with app.app_context():
    #     from app.themes import themes

    from app.admin_views import UserView, PostView, DraftView, CommentView, PublicationView, TagView, MessageView
    from app.models import User, Post, Draft, Comment, Publication, Tag, Message
    admin.add_view(UserView(User, db.session, name='Users', endpoint='users'))
    admin.add_view(PostView(Post, db.session, name='Posts', endpoint='posts'))
    admin.add_view(DraftView(Draft, db.session, name='Drafts', endpoint='drafts'))
    admin.add_view(CommentView(Comment, db.session, name='Comments', endpoint='comments'))
    admin.add_view(PublicationView(Publication, db.session, name='Publications', endpoint='publications'))
    admin.add_view(TagView(Tag, db.session, name='Tags', endpoint='Tags'))
    admin.add_view(MessageView(Message, db.session, name='Messages', endpoint='messages'))

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
