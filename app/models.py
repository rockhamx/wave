import bleach
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from markdown import markdown
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
import jwt
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin

from app import db, login_manager
from datetime import datetime
from time import time
from hashlib import md5

# per_page =

follows = db.Table('follows',
                   db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                   db.Column('following_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                   db.Column('timestamp', db.DateTime, default=datetime.utcnow)
                   )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    description = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    email_hash = db.Column(db.String(32))
    locale = db.Column(db.String(8), default='en_US')
    timezone = db.Column(db.String(8), default='UTC+8')
    is_administrator = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', lazy='dynamic', backref=db.backref('author', lazy='select'))
    comments = db.relationship('Comment', lazy='dynamic',
                               backref=db.backref('author', lazy='select'))
    tags = db.relationship('Tag', secondary='users_tags', lazy='subquery',
                           backref=db.backref('users', lazy=True))
    following = db.relationship('User', secondary='follows', lazy='dynamic',
                               primaryjoin=(follows.c.follower_id == id),
                               secondaryjoin=(follows.c.following_id == id),
                               backref=db.backref('followers', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.email_hash is None:
            self.email_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password is not readable.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm_id': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return False
        if self.id != data.get('confirm_id'):
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_email_change_token(self, new_email, expires_in=600):
        return jwt.encode(
            {'change_email': self.id, 'new_email': new_email, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        ).decode('utf-8')

    def change_email(self, token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')['change_email']
            new_email = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')['new_email']
        except:
            return False
        if self.id != id:
            return False
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.email_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar_hash(self):
        return md5(self.email.lower().encode('utf-8')).hexdigest()

    def avatar(self, size):
        # if self.email_hash is None:
        #     self.email_hash = self.gravatar_hash()
        #     db.session.add(self)
        #     db.session.commit()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(self.email_hash, size)

    def is_following(self, user):
        return self.following.filter(
            follows.c.following_id == user.id).count() > 0

    def follows(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def un_follows(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def following_desc_by_time(self):
        return self.following.order_by(follows.c.timestamp).all()

    def followers_desc_by_time(self):
        return self.followers.order_by(follows.c.timestamp).all()

    def followed_posts(self, page):
        return Post.query.join(
            follows, (follows.c.following_id == Post.author_id)).filter(
            follows.c.follower_id == self.id).order_by(
            Post.pub_timestamp.desc()).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            error_out=False
        ).items

    def recent_posts(self):
        followed = Post.query.join(
            follows, (follows.c.following_id == Post.author_id)).filter(
                follows.c.follower_id == self.id)
        own = Post.query.filter_by(author_id=self.id)
        return followed.union(own).order_by(Post.pub_timestamp.desc())

    @staticmethod
    def search(page=1, name_pattern='%%', description_pattern='%%'):
        return User.query.filter(
            User.name.ilike(name_pattern) |
            User.description.ilike(description_pattern)
        ).paginate(
            page, per_page=10,
            error_out=False
        ).items


class AnonymousUser(AnonymousUserMixin):
    is_administrator = False


login_manager.anonymous_user = AnonymousUser


Users_Tags = db.Table('users_tags',
                      db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                      db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
                      )


Posts_Tags = db.Table('posts_tags',
                      db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
                      db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
                      )


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(128))
    posts = db.relationship('Post', lazy='dynamic',
                            backref=db.backref('category', lazy='select'))


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    description = db.Column(db.String(128))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle = db.Column(db.String(80), nullable=True)
    description = db.Column(db.String(256), nullable=True)
    body = db.Column(db.Text(), nullable=False)
    html = db.Column(db.Text())
    preview = db.Column(db.Text())
    is_public = db.Column(db.Boolean(), nullable=False)
    pub_timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    edit_timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    language = db.Column(db.String(5), default='en')
    clicked = db.Column(db.Integer, default=0)
    hearts = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    tags = db.relationship('Tag', secondary='posts_tags', lazy='subquery',
                           backref=db.backref('posts', lazy=True))
    comments = db.relationship('Comment', lazy='dynamic',
                               backref=db.backref('post', lazy='select'))

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)

    def click(self):
        self.clicked += 1

    @staticmethod
    def newest(page=1):
        return Post.query.order_by(Post.pub_timestamp.desc()).paginate(
            page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            error_out=False
        ).items

    @staticmethod
    def search(page=1, title_pattern='%%', subtitle_pattern='%%', description_pattern='%%'):
        return Post.query.filter(
            Post.title.ilike(title_pattern) |
            Post.subtitle.ilike(subtitle_pattern) |
            Post.preview.ilike(description_pattern)
        ).order_by(Post.pub_timestamp.desc()).paginate(
            page, per_page=10,
            error_out=False
        ).items

    # @db.event.listen_for(Post.body, 'set', Post.on_cha)
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        # update edit timestamp
        target.edit_timestamp = datetime.utcnow()
        # add languages guessing
        try:
            target.language = detect(value)
        except LangDetectException:
            target.language = ''
        # rendering html
        allowed_tags = current_app.config['WAVE_ALLOWED_TAGS']
        md = markdown(value, output_format='html')
        target.html = bleach.linkify(bleach.clean(md, tags=allowed_tags))
        # preview of post, extract first 64 words
        cleaned = bleach.clean(md, tags=[], strip=True)
        nth_words = 64
        # 中文
        if 'zh' in target.language:
            preview = cleaned[:nth_words]
        # latin
        else:
            index = 0
            try:
                for _ in range(nth_words):
                    index = cleaned.index(' ', index + 1)
                target.preview = cleaned[:index] + '...'
            except ValueError:
                target.preview = cleaned[:index]


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    pub_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    edit_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)


class Hearts(db.Model):
    __tablename__ = 'hearts'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# TODO: draft table
# class Draft(db.Model):


# TODO: preference table
# class UserPreference(db.Model):
    # pass


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
