import os
import yaml

class Config:
    # Load database configuration from db.yaml
    with open('db.yaml') as f:
        db = yaml.safe_load(f)

    MYSQL_HOST = db['mysql_host']
    MYSQL_USER = db['mysql_user']
    MYSQL_PASSWORD = db['mysql_password']
    MYSQL_DB = db['mysql_db']
    MYSQL_CURSORCLASS = 'DictCursor'

    SECRET_KEY = os.urandom(24)

    # This is the folder where the uploaded photos will be saved
    UPLOAD_FOLDER = 'static/uploads'