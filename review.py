import mysql.connector
from mysql.connector import Error
import yaml

#DB configuration
db = yaml.safe_load(open('db.yaml'))

def connect(db_name):
    return mysql.connector.connect(
        host = db['mysql_host'],
        user = db['mysql_user'],
        password = db['mysql_password'],
        database = db_name
    )
    
def create_connection(host_name = db['mysql_host'],user_name =  db['mysql_user'], db_password = db['mysql_password']):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=db_password,
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection
    

def create_table():
    database_name = 'mytravelapp_reviews'
    with create_connection() as conn:
        c = conn.cursor()
        c.execute("CREATE DATABASE IF NOT EXISTS mytravelapp_reviews")
        c.execute("USE mytravelapp_reviews")
        c.execute('''CREATE TABLE IF NOT EXISTS reviews
            (id INTEGER PRIMARY KEY AUTO_INCREMENT,
             country TEXT NOT NULL,
             text TEXT NOT NULL,
             photo TEXT,
             rating INTEGER DEFAULT 0)
        ''')
        conn.commit()

def add_review(country, text, photo_filename):
    with connect('mytravelapp_reviews') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO reviews (country, text, photo) VALUES (%s, %s, %s)', (country, text, photo_filename))
        conn.commit()

def get_all_reviews():
    try:
        create_table()
        with connect('mytravelapp_reviews') as conn:
            c = conn.cursor()
            c.execute('SELECT country, text, photo FROM reviews')
            reviews = [{'country': row[0], 'text': row[1], 'photo': row[2]} for row in c.fetchall()]
    except:
        ...
    return reviews

def add_rating(review_id, rating):
    with connect() as conn:
        c = conn.cursor()
        c.execute('UPDATE reviews SET rating = %s WHERE id = %s', (rating, review_id))
        conn.commit()

def get_rating(review_id):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT rating FROM reviews WHERE id = %s', (review_id,))
        rating = c.fetchone()
    return rating[0] if rating else None