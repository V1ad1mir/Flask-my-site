import mysql.connector
from mysql.connector import Error
import yaml
import datetime
import folium
import pandas as pd
import re

def connect():
    #DB configuration
    with open('db.yaml') as f:
        db = yaml.safe_load(f)
    try:
        return mysql.connector.connect(
            host = db['mysql_host'],
            user = db['mysql_user'],
            password = db['mysql_password'],
            database = db['mysql_db']
        )
    except Error as e:
        print(f"The error '{e}' occurred")
    
def set_answer_for_question(question_id, answer, author_ans):
    with connect() as conn:
        c = conn.cursor()
        c.execute('UPDATE community_questions SET answer = %s, author_ans = %s WHERE id = %s', (answer, author_ans, question_id))
        conn.commit()
    
def register_user(name,mail, password, date_of_birth,  country, avatar):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                (
                id INT NOT NULL AUTO_INCREMENT,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                date_of_birth DATE,
                country VARCHAR(50),
                avatar VARCHAR(255),
                PRIMARY KEY (id)
                ); ''')
        # Execute the SQL query to insert the user's information into the "users" table
        c.execute("INSERT INTO users (username, password, email,  date_of_birth, country, avatar) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, password, mail, date_of_birth,  country, avatar))
        conn.commit()
    
def add_community_question(question,author_que):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS community_questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question VARCHAR(255) NOT NULL,
        answer VARCHAR(255) ,
        author_que VARCHAR(255) NOT NULL,
        author_ans VARCHAR(255) ,
        date DATE NOT NULL
        );''')
        date = datetime.date.today()
        # Insert the question, answer, and author into the table
        add_question = ("INSERT INTO community_questions "
                        "(question, author_que, date) "
                        "VALUES (%s, %s, %s)")
        data_question = (question, author_que, date)
        c.execute(add_question, data_question)
        conn.commit()

def create_map():
    # create a connection to the database
    with connect() as conn:
        cursor = conn.cursor()
        # execute the SQL query to retrieve the travel data
        cursor.execute("""
        SELECT country, COUNT(*) AS count
        FROM travel
        GROUP BY country
        """)

        # create a pandas DataFrame from the query result
        df = pd.DataFrame(cursor.fetchall(), columns=['country', 'count'])
        

        # create a map with the folium library
        map = folium.Map(location=[0, 0], zoom_start=2)

        import json
        # Load the GeoJSON file
        with open('countries.geo.json', 'r') as f:
            geojson_data = json.load(f)
        # add the choropleth layer to the map to colorize the countries
        # Create the choropleth layer
        folium.Choropleth(
            geo_data=geojson_data,
            name='choropleth',
            data=df,
            columns=['country', 'count'],
            key_on='feature.properties.name',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Travel data'
        ).add_to(map)

        # add the layer control to the map
        folium.LayerControl().add_to(map)
    # return the map as HTML
    return map

def add_review(country, text, photo_filename, author):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS reviews
        (
        id INT AUTO_INCREMENT PRIMARY KEY,
        country VARCHAR(255) NOT NULL,
        text TEXT NOT NULL,
        photo VARCHAR(255),
        rating_total INT DEFAULT 0,
        rating_count INT DEFAULT 0,
        author VARCHAR(255) NOT NULL,
        date DATE NOT NULL
        );
        ''')
        date = datetime.date.today()
        c.execute('INSERT INTO reviews (country, text, photo, author, date) VALUES (%s, %s, %s, %s, %s)', (country, text, photo_filename, author, date))
        conn.commit()
       
def add_trip(user_name, country, month, year, cities, duration, budget, rating):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS travel 
        (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_name VARCHAR(255) NOT NULL,
        country VARCHAR(255) NOT NULL,
        month INT NOT NULL,
        year INT NOT NULL,
        cities VARCHAR(255) NOT NULL,
        duration INT NOT NULL,
        budget DECIMAL(10, 2),
        rating INT
        );
        ''')
        query = ("INSERT INTO travel"
                "(user_name, country, month, year, cities, duration, budget, rating)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        values = (user_name, country, month, year, cities, duration, budget, rating)
        print(values)
        c.execute(query, values)
        conn.commit()

def delete_review(review_id):
    with connect() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM reviews WHERE id = %s', (review_id,))
        conn.commit()
        
def update_rating(review_id, rating):
    """
    Update the rating for the review with the given ID.

    Args:
        review_id: The ID of the review to update.
        rating: The new rating to assign to the review.

    Returns:
        None
    """
    with connect() as conn:
        c = conn.cursor()
        # Calculate the total rating and rating count for the review
        c.execute('SELECT rating_total, rating_count FROM reviews WHERE id = %s', (review_id,))
        result = c.fetchone()
        if result is not None:
            rating_total = result[0] + rating
            rating_count = result[1] + 1
            # Update the rating and rating count
            c.execute('UPDATE reviews SET rating_total = %s, rating_count = %s WHERE id = %s',
                           (rating_total, rating_count, review_id))
        conn.commit()

def get_rating(review_id):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT rating FROM reviews WHERE id = %s', (review_id,))
        rating = c.fetchone()
    return rating[0] if rating else None

def correct_mail_address(email):
    return re.match(r'[^@]+@[^@]+\.[^@]+', email)
