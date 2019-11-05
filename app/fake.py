from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models import User, Post


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='123',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 description=fake.text(),
                 member_since=fake.past_date(),
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


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1,)).first()
        p = Post(title=fake.sentence(),
                 body='/n'.join(fake.texts(nb_texts=10)),
                 is_public=False,
                 pub_timestamp=fake.past_date(),
                 author=u
                 )
        db.session.add(p)
    db.session.commit()
