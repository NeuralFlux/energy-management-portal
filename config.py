import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
SECRET_KEY = 'my precious'

MYSQL_USER_ID = os.environ.get("MYSQL_USER")
MYSQL_PASSWD = os.environ.get("MYSQL_PASSWD")
