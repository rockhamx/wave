import os
import json

from flask import current_app


themes = [
    ('/css/bootstrap.min.css', 'Original - Default'),
]
with open(os.path.join(current_app.instance_path, 'bootswatch.json'), 'r') as fp:
    bootswatch = json.load(fp)
    for index, theme in enumerate(bootswatch['themes'], start=1):
        themes.append((theme['css'], '{} - {}'.format(theme['name'], theme['description'])))


with open(os.path.join(current_app.instance_path, 'bootswatch.py'), 'w') as fp:
    fp.write(str(themes))
