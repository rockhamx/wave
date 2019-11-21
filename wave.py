import os, click
from app import create_app, bootstrap, db, mail, migrate, babel, moment
from app.models import User, Tag, Post, Users_Tags, Posts_Tags, Comment, Heart, Publication, Bookmark
from app.email import send_email

app = create_app(os.getenv('FLASK_ENV'))


@app.shell_context_processor
def shell():
    return dict(app=app,
                db=db,
                bootstrap=bootstrap,
                migrate=migrate,
                mail=mail,
                moment=moment,
                babel=babel,
                User=User, Post=Post, Tag=Tag, Publication=Publication, Comment=Comment,
                Heart=Heart, Bookmark=Bookmark,
                UT=Users_Tags, PT=Posts_Tags,
                send_email=send_email)


@app.cli.group()
def trans():
    """Translation and localization commands."""
    pass


@trans.command()
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')


@trans.command()
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')


@trans.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system(
            'pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')


if __name__ == '__main__':
    app.run()
