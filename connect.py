import mysql.connector
from mysql.connector import Error
import yaml

def connect():
    # Load DB configuration from file
    with open('db.yaml') as f:
        db = yaml.safe_load(f)
    # Connect to database
    try:
        connection = mysql.connector.connect(
            host=db['mysql_host'],
            user=db['mysql_user'],
            password=db['mysql_password'],
            database=db['mysql_db']
        )
        return connection
    except Error as e:
        raise Exception(f"Could not connect to database. Error: {e}")