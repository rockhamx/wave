import os
from app import create_app, bootstrap, db, mail, migrate, moment
from app.models import User, Tag, Post, Users_Tags, Posts_Tags
from app.email import send_email

app = create_app(os.getenv('FLASK_ENV') or 'default')


@app.shell_context_processor
def shell():
    return dict(app=app,
                db=db,
                bootstrap=bootstrap,
                migrate=migrate,
                mail=mail,
                moment=moment,
                User=User, Tag=Tag, Post=Post, UT=Users_Tags, PT=Posts_Tags,
                send_email=send_email)


if __name__ == '__main__':
    app.run()