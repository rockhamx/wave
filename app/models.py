from threading import Thread

from PIL import Image
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
import jwt
import bleach
import requests
import os.path
from flask import current_app, jsonify, url_for
from flask_login import UserMixin, AnonymousUserMixin

from app import db, login_manager
from config import Config
from datetime import datetime
from time import time
from hashlib import md5

follows = db.Table('follows',
                   db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                   db.Column('following_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                   db.Column('timestamp', db.DateTime, default=datetime.utcnow)
                   )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, nullable=False, index=True)
    location = db.Column(db.String(64))
    description = db.Column(db.Text)
    confirmed = db.Column(db.Boolean, default=False)
    locale = db.Column(db.String(12), default='en_US')
    timezone = db.Column(db.String(8), default='UTC+8')
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(128), nullable=False)
    email_hash = db.Column(db.String(32))
    theme = db.Column(db.String(256))
    is_administrator = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', lazy='dynamic', backref=db.backref('author', lazy='select'))
    comments = db.relationship('Comment', lazy='dynamic',
                               backref=db.backref('author', lazy='select'))
    following = db.relationship('User', secondary='follows', lazy='dynamic',
                                primaryjoin=(follows.c.follower_id == id),
                                secondaryjoin=(follows.c.following_id == id),
                                backref=db.backref('followers', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.name:
            self.name = self.username
        if self.email and self.email_hash is None:
            self.email_hash = self.gravatar_hash()
        for size in Config.WAVE_AVATAR_REQUIRED_SIZE:
            self.download_gravatar_async(size=size)

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

    def gravatar_url(self, size=''):
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(self.email_hash, size)

    def avatar_dir(self):
        return os.path.join(current_app.root_path, 'static', 'images', 'users', self.email_hash, 'avatar')

    def avatar_path(self, dirname=None, size=None):
        if not dirname:
            dirname = self.avatar_dir()
        if size:
            return os.path.join(dirname, '{}x{}.png'.format(size, size))
        else:
            return os.path.join(dirname, 'default.png')

    def save_upload_avatar(self, file_storage):
        default_filepath = self.avatar_path()
        if os.path.splitext(file_storage.filename)[1] != '.png':
            default = Image.open(file_storage.stream)
            default.save(default_filepath)
        else:
            file_storage.save(default_filepath)

        for size in Config.WAVE_AVATAR_REQUIRED_SIZE:
            filepath = self.avatar_path(size=size)
            im = Image.open(default_filepath).copy().resize((size, size))
            im.save(filepath)

    @staticmethod
    def download_image(url, filepath):
        r = requests.get(url)
        # assert r.status_code == 200
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(r.content)
                return True
        return False

    def download_gravatar_async(self, filepath=None, size=None):
        if not filepath:
            filepath = self.avatar_path(size=size)
        url = self.gravatar_url(size)
        thr = Thread(target=self.download_image, args=(url, filepath))
        thr.start()
        return thr

    def avatar(self, size=None):
        dirname = self.avatar_dir()
        abs_filepath = self.avatar_path(dirname, size)
        if not os.path.exists(abs_filepath):
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            self.download_gravatar_async(abs_filepath, size)
            return self.gravatar_url(size)

        filename = self.avatar_path(os.path.join('images', 'users', self.email_hash, 'avatar'), size)
        return url_for('static', filename=filename)

    def drafts_desc_by_time(self, page):
        return self.drafts.order_by(
            Draft.saved_timestamp.desc(), Draft.created_timestamp.desc()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def latest_posts(self, page=1):
        return self.posts.order_by(
            Post.edit_timestamp.desc()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def latest_posts_exclude_private(self, page=1):
        return self.posts.filter(
            Post.is_public == 1
        ).order_by(
            Post.edit_timestamp.desc()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def private_posts(self, page):
        return self.posts.filter(
            Post.is_public != 1
        ).order_by(
            Post.edit_timestamp.desc()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def followed_posts(self, page=1):
        return Post.query.join(
            follows, (Post.author_id == follows.c.following_id)
        ).filter(
            Post.is_public == 1, follows.c.follower_id == self.id
        ).order_by(
            Post.pub_timestamp.desc()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
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
            # error_out=False
        ).items

    def following_desc_by_time(self):
        return self.following.order_by(follows.c.timestamp).all()

    def followers_desc_by_time(self):
        return self.followers.order_by(follows.c.timestamp).all()

    def follows(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def un_follows(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(
            follows.c.following_id == user.id).count() > 0

    def hearts_desc_by_time(self, page=1):
        return Post.query.join(
            Heart, (Post.id == Heart.post_id)
        ).filter(
            Heart.user_id == self.id
        ).order_by(
            Heart.timestamp.desc()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def like(self, post, amount=1):
        heart = Heart.query.filter_by(user_id=self.id, post_id=post.id).first()
        if heart:
            heart.amount += 1
            post.hearts += 1
            heart.timestamp = datetime.utcnow()
            # return True
        else:
            heart = Heart(amount=amount,
                          user_id=self.id,
                          post_id=post.id)
            post.hearts += 1
        db.session.add(heart)

    def unlike(self, post):
        heart = Heart.query.filter_by(user_id=self.id, post_id=post.id).first()
        if heart:
            post.hearts -= heart.amount
            return self.hearted.remove(heart)
        else:
            return False

    # return type:int
    def hearts_amount(self, post):
        heart = Heart.query.filter_by(user_id=self.id, post_id=post.id).first()
        if heart:
            return heart.amount
        else:
            return 0

    def bookmarks_desc_by_time(self, page=1):
        return Post.query.join(
            Bookmark, (Post.id == Bookmark.post_id)
        ).filter(
            Bookmark.user_id == self.id
        ).order_by(
            Bookmark.timestamp
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def add_bookmark(self, post):
        # associate with bookmark instance
        bookmark = Bookmark.query.filter_by(user_id=self.id, post_id=post.id).first()
        if bookmark:
            return False
        bookmark = Bookmark(user_id=self.id, post_id=post.id)
        db.session.add(bookmark)
        return True
        #     bookmarks = Bookmark(timestamp=datetime.utcnow())
        # bookmarks.user = self
        # self.bookmarks.append(post)
        # db.session.commit()

    def remove_bookmark(self, post):
        bookmark = Bookmark.query.filter_by(user_id=self.id, post_id=post.id).first()
        if bookmark:
            db.session.delete(bookmark)
            return True
        return False

    def is_bookmarked(self, post):
        return post.id in [bookmark.post_id for bookmark in self.bookmarks]

    def followed_pubs_desc_by_time(self, page=1):
        return Publication.query.join(
            FollowedPublication, (Publication.id == FollowedPublication.publication_id)
        ).filter(
            FollowedPublication.user_id == self.id
        ).order_by(
            Publication.created_timestamp.desc()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def recommend_pubs_desc_by_popular(self, page=1):
        return Publication.query.join(
            FollowedPublication, (Publication.id == FollowedPublication.publication_id)
        ).filter(
            # FollowedPublication.user_id != self.id
        ).order_by(
            Publication.created_timestamp.desc()
            # Publication.posts.count()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def follow_publication(self, pub):
        followed_pub = FollowedPublication.query.filter_by(user_id=self.id, publication_id=pub.id).first()
        if followed_pub:
            return False
        followed_pub = FollowedPublication(user_id=self.id, publication_id=pub.id)
        db.session.add(followed_pub)
        return True

    def unfollow_publication(self, pub):
        followed_pub = FollowedPublication.query.filter_by(user_id=self.id, publication_id=pub.id).first()
        if followed_pub:
            db.session.delete(followed_pub)
            return True
        return False

    def comments_desc_by_time(self, page=1):
        return self.comments.order_by(
            Comment.pub_timestamp.desc()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def unread_messages_count(self):
        return self.message_received.filter(
            Message.read == 0
        ).count()

    def messages_sent_desc_by_time(self):
        return self.message_sent.order_by(
            Message.timestamp.desc()
        ).all()

    def messages_received_asc_by_time(self):
        return self.message_received.order_by(
            Message.read.asc()).order_by(
            Message.timestamp.desc()
        ).all()


class AnonymousUser(AnonymousUserMixin):
    is_administrator = False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    subtitle = db.Column(db.String(128), nullable=True)
    description = db.Column(db.String(256), nullable=True)
    hearts = db.Column(db.Integer, default=0)
    language = db.Column(db.String(8), default='en')
    is_public = db.Column(db.Boolean(), nullable=False, default=1)
    body = db.Column(db.Text())
    html = db.Column(db.Text())
    preview = db.Column(db.Text())
    publication = db.relationship('Publication', lazy='select',
                                  backref=db.backref('posts', lazy='dynamic', uselist=True))
    pub_timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    edit_timestamp = db.Column(db.DateTime(), index=True)
    clicked = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    tags = db.relationship('Tag', secondary='posts_tags', lazy='subquery',
                           backref=db.backref('posts', lazy=True))
    comments = db.relationship('Comment', lazy='dynamic', cascade="all, delete-orphan",
                               backref=db.backref('post', lazy='select'))

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)

    def click(self):
        self.clicked += 1

    @staticmethod
    def to_json():
        pass

    @staticmethod
    def from_json(post, type='html'):
        if getattr(post, 'id', None):
            return Post.query.get(post.id)
        if type == 'html':
            return Post(title=post.get('title'), subtitle=post.get('subtitle', None),
                        description=post.get('description', None), html=post.get('content'),
                        is_public=post.get('isPublic'))
        elif type == 'markdown':
            pass

    def update(self, title, subtitle, description, is_public, tags, body=None, html=None):
        if title:
            self.title = title
        self.subtitle = subtitle
        self.description = description
        self.is_public = 1 if is_public else 0
        self.tags = tags
        if body:
            self.body = body
        else:
            self.html = html
        # self.edit_timestamp = datetime.utcnow()

    @staticmethod
    def newest(page=1):
        return Post.query.filter(
            Post.is_public == 1
        ).order_by(
            Post.pub_timestamp.desc()
        ).paginate(
            page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    @staticmethod
    def search(page=1, title_pattern='%%', subtitle_pattern='%%', description_pattern='%%'):
        return Post.query.filter(
            Post.title.ilike(title_pattern) |
            Post.subtitle.ilike(subtitle_pattern) |
            Post.preview.ilike(description_pattern)
        ).order_by(Post.pub_timestamp.desc()).paginate(
            page, per_page=10,
            # error_out=False
        ).items

    def comments_desc_by_time(self, page=1):
        return self.comments.order_by(
            Comment.pub_timestamp.desc()).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    # @db.event.listen_for(Post.body, 'set', Post.on_cha)
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        # render markdown to html
        if value:
            html = markdown(value, output_format='html')
        else:
            html = ''
        target.html = html

    @staticmethod
    def on_changed_html(target, value, oldvalue, initiator):
        # set or update edit timestamp
        if target.edit_timestamp:
            target.edit_timestamp = datetime.utcnow()
        else:
            target.edit_timestamp = target.pub_timestamp = datetime.utcnow()
        # filtering some html tags
        allowed_tags = Config.WAVE_ALLOWED_TAGS
        value = bleach.linkify(bleach.clean(value, tags=allowed_tags))

        cleaned = bleach.clean(value, tags=[], strip=True)
        # add languages guessing
        try:
            target.language = detect(cleaned)
        except LangDetectException:
            target.language = ''

        # preview of a post, extract first 64 words
        nth_words = 64
        # chinese
        if 'zh' in target.language:
            target.preview = cleaned[:nth_words]
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
db.event.listen(Post.html, 'set', Post.on_changed_html)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    pub_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    edit_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)


class Heart(db.Model):
    __tablename__ = 'hearts'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    amount = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship('User', single_parent=True,
                           backref=db.backref('hearted', lazy='dynamic', cascade="all, delete-orphan"))
    post = db.relationship('Post', single_parent=True,
                           backref=db.backref('hearted_users', lazy='dynamic', cascade="all, delete-orphan"))


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', single_parent=True,
                           backref=db.backref('bookmarks', lazy='dynamic', cascade="all, delete-orphan"))
    post = db.relationship('Post', single_parent=True,
                           backref=db.backref('bookmarked_users', lazy='dynamic', cascade="all, delete-orphan"))


class Publication(db.Model):
    __tablename__ = "publications"
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(512))
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.String(128), default='')
    created_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator = db.relationship('User', lazy='select')

    @staticmethod
    def exist(name):
        return Publication.query.filter_by(name=name).first()

    @staticmethod
    def search(page=1, name_pattern='%%', description_pattern='%%'):
        return Publication.query.filter(
            Publication.name.ilike(name_pattern) |
            Publication.description.ilike(description_pattern)
        ).order_by(Publication.created_timestamp.desc()).paginate(
            page, per_page=10,
            # error_out=False
        ).items


class FollowedPublication(db.Model):
    __tablename__ = 'followed_publications'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', single_parent=True,
                           backref=db.backref('followed_publications', lazy='dynamic', cascade="all, delete-orphan"))
    publication = db.relationship('Publication', single_parent=True,
                                  backref=db.backref('followed_users', lazy='dynamic', cascade="all, delete-orphan"))


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    description = db.Column(db.String(128), default='')
    created_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.name

    @staticmethod
    def get_or_create(name, description=""):
        if not name:
            return None
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name, description=description)
        return tag

    @staticmethod
    def search(page=1, name_pattern='%%', description_pattern='%%'):
        return Tag.query.filter(
            Tag.name.ilike(name_pattern) |
            Tag.description.ilike(description_pattern)
        ).order_by(Tag.created_timestamp.desc()).paginate(
            page, per_page=10,
            # error_out=False
        ).items

    # @staticmethod
    # def addTags(names=[], descriptions=[]):
    #     if not len(names):
    #         return []
    #     if not len(descriptions):
    #         for _ in range(len(names)):
    #             descriptions.append("")
    #
    #     tags = []
    #     for name, des in names, descriptions:
    #         tag = Tag.query.filter_by(name=name).first()
    #         if tag:
    #             continue
    #         tag = Tag(name=name, description=des)
    #         tags.append(tag)
    #     return tags


class Message(db.Model):
    # __tablename__
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    read = db.Column(db.Boolean, index=True, default=False)
    content = db.Column(db.String(256))
    sender = db.relationship('User', lazy='select', foreign_keys=[sender_id],
                             backref=db.backref('message_sent', lazy='dynamic',
                                                cascade='all, delete-orphan'))
    recipient = db.relationship('User', lazy='select', foreign_keys=[recipient_id],
                                backref=db.backref('message_received', lazy='dynamic',
                                                   cascade='all, delete-orphan'))


Posts_Tags = db.Table('posts_tags',
                      db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
                      db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
                      )


class Draft(db.Model):
    # __tablename__ =
    id = db.Column(db.Integer, primary_key=True)
    reference_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    title = db.Column(db.String(128))
    subtitle = db.Column(db.String(128))
    description = db.Column(db.String(256))
    content = db.Column(db.Text)
    is_public = db.Column(db.Boolean(), nullable=False, default=True)
    type = db.Column(db.String(16), nullable=False)
    tags = db.Column(db.String(256))
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    saved_timestamp = db.Column(db.DateTime(), index=True)
    author = db.relationship('User', lazy='select',
                             backref=db.backref('drafts', lazy='dynamic'))
    post = db.relationship('Post', lazy=True,
                           backref=db.backref('drafts', lazy='dynamic'))

    def bleach(self, content):
        return bleach.clean(content, tags=[], strip=True)

    def to_json(self):
        return jsonify({
            "result": "success",
            "id": self.id,
            "reference_id": self.reference_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "type": self.type,
            "content": self.content,
            "created_timestamp": self.created_timestamp,
            "saved_timestamp": self.saved_timestamp,
            "tags": self.tags,
            "is_public": self.is_public,
        })

    @staticmethod
    def from_json(draft):
        if draft.get('id', None):
            return Draft.query.get(draft['id'])
        else:
            return Draft(reference_id=draft.get('reference_id', None),
                         type=draft.get('type'),
                         title=draft.get('title', None),
                         subtitle=draft.get('subtitle', None),
                         description=draft.get('description', None),
                         content=draft.get('content', None),
                         is_public=draft.get('is_public', True),
                         tags=draft.get('tags', None)
                         )

    def update_from_json(self, draft):
        title = draft.get('title', None)
        subtitle = draft.get('subtitle', None)
        description = draft.get('description', None)
        type = draft.get('type', None)
        content = draft.get('content', None)
        is_public = draft.get('is_public', None)
        tags = draft.get('tags', None)
        self.update(title=title, subtitle=subtitle, description=description, type=type, content=content,
                    is_public=is_public, tags=tags)

    def update(self, title=None, subtitle=None, description=None, type=None, content=None, is_public=None, tags=None):
        if title:
            self.title = title
        if subtitle:
            self.subtitle = subtitle
        if description:
            self.description = description
        if type:
            self.type = type
        if content:
            self.content = content
        if is_public:
            self.is_public = is_public
        if tags:
            self.tags = tags
        self.saved_timestamp = datetime.utcnow()

# class UserPreference(db.Model):
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
#     theme = db.Column(db.String(16))
# user = db.relationship('User', lazy=True,
#                        backref=db.backref('preference', lazy=True))
