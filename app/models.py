import bleach
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
import jwt
from flask import current_app, jsonify
from flask_login import UserMixin, AnonymousUserMixin

from app import db, login_manager
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
    locale = db.Column(db.String(12), default='en_US')
    timezone = db.Column(db.String(8), default='UTC+8')
    is_administrator = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', lazy='dynamic', backref=db.backref('author', lazy='select'))
    comments = db.relationship('Comment', lazy='dynamic',
                               backref=db.backref('author', lazy='select'))
    # tags = db.relationship('Tag', secondary='users_tags', lazy='subquery',
    #                        backref=db.backref('user', lazy=True))
    # publications = db.relationship('Publication', backref=db.backref('authors', lazy='dynamic'))
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
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(self.email_hash, size)

    def drafts_desc_by_time(self, page):
        return self.drafts.order_by(
            Draft.saved_timestamp.desc(), Draft.created_timestamp.desc()
        ).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def latest_posts(self, page=1):
        return self.posts.order_by(Post.edit_timestamp.desc()).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items

    def followed_posts(self, page=1):
        return Post.query.join(
            follows, (Post.author_id == follows.c.following_id)
        ).filter(
            follows.c.follower_id == self.id
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
        return post.id in [b.post_id for b in self.bookmarks]

    def followed_pubs_desc_by_time(self, page=1):
        return Publication.query.join(
            FollowedPublication, (Publication.id == FollowedPublication.publication_id)
        ).filter(
            FollowedPublication.user_id == self.id
        ).order_by(
            Publication.created_timestamp
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
    body = db.Column(db.Text())
    html = db.Column(db.Text())
    preview = db.Column(db.Text())
    is_public = db.Column(db.Boolean(), nullable=False)
    pub_timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    edit_timestamp = db.Column(db.DateTime(), index=True)
    language = db.Column(db.String(8), default='en')
    clicked = db.Column(db.Integer, default=0)
    hearts = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    comments = db.relationship('Comment', lazy='dynamic', cascade="all, delete-orphan",
                               backref=db.backref('post', lazy='select'))
    publication = db.relationship('Publication', lazy='select',
                                  backref=db.backref('posts', lazy='dynamic', uselist=True))
    tags = db.relationship('Tag', secondary='posts_tags', lazy='subquery',
                           backref=db.backref('posts', lazy=True))

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

    def update(self, title=None, subtitle=None, description=None, body=None, html=None, is_public=None, tags=None):
        if title:
            self.title = title
        if subtitle:
            self.subtitle = subtitle
        if description:
            self.description = description
        if body:
            self.body = body
        if html:
            self.html = html
        if is_public:
            self.is_public = is_public
        if tags:
            self.tags = tags
        # self.edit_timestamp = datetime.utcnow()

    @staticmethod
    def newest(page=1):
        return Post.query.order_by(Post.pub_timestamp.desc()).paginate(
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

    # @db.event.listen_for(Post.body, 'set', Post.on_cha)
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        # render markdown to html
        html = markdown(value, output_format='html')
        target.html = html

    @staticmethod
    def on_changed_html(target, value, oldvalue, initiator):
        # set or update edit timestamp
        if target.edit_timestamp:
            target.edit_timestamp = datetime.utcnow()
        else:
            target.edit_timestamp = target.pub_timestamp = datetime.utcnow()
        # filtering some html tags
        allowed_tags = current_app.config['WAVE_ALLOWED_TAGS']
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

    def comments_desc_by_time(self, page=1):
        return self.comments.order_by(
            Comment.pub_timestamp.desc()).paginate(
            page=page, per_page=current_app.config['WAVE_POSTS_PER_PAGE'],
            # error_out=False
        ).items


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
    content = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    read = db.Column(db.Boolean, index=True, default=False)
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
    type = db.Column(db.String(16), nullable=False)
    content = db.Column(db.Text)
    is_public = db.Column(db.Boolean(), nullable=True)
    tags = db.Column(db.String(256))
    publication_id = db.Column(db.Integer, db.ForeignKey('publications.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    saved_timestamp = db.Column(db.DateTime(), index=True)
    author = db.relationship('User', lazy='select',
                             backref=db.backref('drafts', lazy='dynamic'))

    def to_json(self):
        return jsonify({
            "status": "success",
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

# TODO: preference table
# class UserPreference(db.Model):
# pass
