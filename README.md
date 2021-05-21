# Wave

## Frameworks

- Flask
- SQLAlchemy
- React
- Slate

## Get things started

### Prerequisites

- Python3
- Mysql

Create a virtual environment.
`python3 -m venv venv`

Activative it.
`. venv/bin/activate`(linux)

Install python dependencies for development.
`pip install -r requirements/dev.txt` 
otherwise
`pip install -r requirements/prod.txt`

Install frontend dependencies for development.
`npm install` 
or
`npm install --only=prod` for production

Duplicate the dot env file.
`cp .env_example .env`

### (optional)Use mysql database.
Install [mysqlclient](https://pypi.org/project/mysqlclient/)
Create database.
`mysqladmin -u <> -p create wave`
Put your database url on `DATABASE_URL` field inside `.env` file.

Open a flask shell to initialize SQLAlchemy.
`flask shell`
In the opened Python Interpreter enter:
`db.create_all()`

(optional)Initiate Flask-Migration.
`flask db init`

Compile translation files.
`flask trans compile`

Run application
`flask run`
