from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models import User, Post


def users(count=100, locale='en_US'):
    fake = Faker(locale)
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='123',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 description=fake.text(),
                 member_since=fake.past_datetime(),
                 locale=fake.language_code(),
                 timezone=fake.timezone(),
                 is_administrator=False
                 )
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100, locale='en_US'):
    fake = Faker(locale)
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1,)).first()
        p = Post(title=fake.sentence(),
                 body='/n'.join(fake.texts(nb_texts=100)),
                 is_public=True,
                 pub_timestamp=fake.date_time_this_month(),
                 author=u
                 )
        db.session.add(p)
    db.session.commit()

