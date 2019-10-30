import os
from app import create_app, bootstrap, db, mail, migrate, moment
from app.models import User
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
                User=User,
                send_email=send_email)


if __name__ == '__main__':
    app.run()