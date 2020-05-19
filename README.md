## Create a virtual environment
1. `python3 -m venv venv`
2. `. venv/bin/activate`

## Install libraries or dependencies
1. `pip install -r requirement/requirements.txt` or `pip install -r requirement/development.txt`
2. `npm install --only=prod` for production or `npm install` for development

## Create .env file in the root directory and set up some enviroment variables
1. $`cp .env_example .env`
2. $`vim .env`
3. Enter `FLASK_APP=wave` and `FLASK_ENV=development` or `FLASK_ENV=production`

## Create and update database
- `flask db update`

## Compile flask_babel
- `flask trans compile`

## Run application
- `flask run`
