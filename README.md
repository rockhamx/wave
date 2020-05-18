## Create a virtual environment
1. `python3 -m venv venv`
2. run `. venv/bin/activate` on Linux or `./venv/bin/activate.bat` on Windows

# install dependencies
- `pip install -r requirement/requirements.txt` or `pip install -r requirement/development.txt`
- `npm install` or 

# setting up environment variables
- `FLASK_APP=Wave`
- `FLASK_ENV=development` or `FLASK_ENV=production`

# set up .env file in the root directory

# update the database
- `flask db update`

# compile flask_babel
- `flask trans compile`
