## Create a virtual environment
1. `python3 -m venv venv`
2. `. venv/bin/activate`

## Install libraries or dependencies
1. `pip install -r requirement/requirements.txt` or `pip install -r requirement/development.txt`
2. `npm install --only=prod` for production or `npm install` for development
3. install some mysqlclient [prerequisites](https://pypi.org/project/mysqlclient/)

## Create .env file in the root directory and set up some enviroment variables
1. `cp .env_example .env`
2. `vim .env`

## Create the database
1. `mysqladmin -u <> -p create wave`
2. `flask shell`
3. In Python Interpreter enter `db.create_all()`

## (optional)Initiate Flask-Migration
1. `flask db init`

## (optional)Compile translation files
- `flask trans compile`

## Run application
- `flask run`
