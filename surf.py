import os
from app import create_app, bootstrap


app = create_app(os.getenv('FLASK_ENV') or 'default')

@app.shell_context_processor
def shell():
    return dict(app=app, bootstrap=bootstrap)

if __name__ == '__main__':
    app.run()