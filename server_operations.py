import mysql.connector
from mysql.connector import Error
import yaml

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

def get_all_community_questions():
    with connect() as conn:
        c = conn.cursor()
        query = "SELECT * FROM community_questions;"
        c.execute(query)
        data = c.fetchall()
        # Convert the data to a list of dictionaries
        community_questions = []
        for row in data:
            travel = {}
            travel['id'] = row[0]
            travel['question'] = row[1]
            travel['answer'] = row[2]
            travel['author_que'] = row[3]
            travel['author_ans'] = row[4]
            travel['date'] = row[5]
            community_questions.append(travel)
        return community_questions
    
def get_all_reviews():
    try:
        with connect() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM reviews')
            rows = c.fetchall()
            reviews = []
            for row in rows:
                review = {
                    'id': row[0],
                    'country': row[1],
                    'text': row[2],
                    'photo': row[3],
                    'rating': row[4],
                    'author': row[6],
                    'date': row[7],
                }
                # Calculate the average rating for the review
                if row[5] > 0:
                    average_rating = row[4] / row[5]
                    review['average_rating'] = '{:.2f}'.format(average_rating)
                else:
                    review['average_rating'] = 0
                reviews.append(review)
    except:
        reviews=[]
    return reviews

def get_my_travels(user_name):
    with connect() as conn:
            c = conn.cursor()
             # Retrieve the travel data for the user
            if(user_name == 'admin'):
                c.execute("SELECT * FROM travel;")
            else:
                c.execute("SELECT * FROM travel WHERE user_name = %s", (user_name,))
            data = c.fetchall()
            # Convert the data to a list of dictionaries
            travels = []
            for row in data:
                travel = {}
                if(user_name == 'admin'):
                    travel['id'] = row[0]
                    travel['user_name'] = row[1]
                travel['country'] = row[2]
                travel['month'] = row[3]
                travel['year'] = row[4]
                travel['cities'] = row[5]
                travel['duration'] = row[6]
                travel['budget'] = row[7]
                travel['rating'] = row[8]
                travel['d'] = row[0]
                travels.append(travel)
            return travels
        
def get_all_users():
    with connect() as conn:
        c = conn.cursor()
        query = "SELECT * FROM users;"
        c.execute(query)
        data = c.fetchall()
        users = []
        for row in data:
            user = {}
            user['id'] = row[0]
            user['username'] = row[1]
            user['password'] = row[2]
            user['email'] = row[3]
            user['date_of_birth'] = row[4]
            user['country'] = row[5]
            user['avatar'] = row[6]
            users.append(user)
        return users
    

def make_query(query):
    with connect() as conn:
        c = conn.cursor()
        c.execute(query)
        conn.commit()