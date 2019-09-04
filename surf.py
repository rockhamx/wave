import os
from app import create_app, bootstrap, db, mail, migrate, moment
from app.models import User

app = create_app(os.getenv('FLASK_ENV') or 'default')


@app.shell_context_processor
def shell():
    return dict(app=app,
                db=db,
                bootstrap=bootstrap,
                migrate=migrate,
                mail=mail,
                moment=moment,
                User=User)


if __name__ == '__main__':
    app.run()