from flask import Flask,render_template,request,session,redirect,flash, url_for
from flask_mysqldb import MySQL
import yaml
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import review
import re
from datetime import datetime, date
import os
from flask import render_template
from random import shuffle
import hashlib

app = Flask(__name__)

#DB configuration
db = yaml.safe_load(open('db.yaml'))

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.urandom(24)

# This is the folder where the uploaded photos will be saved
app.config['UPLOAD_FOLDER'] = 'static/uploads' 






@app.route('/reviews/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    review.delete_review(review_id)
    return redirect(url_for('reviews'))


@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        # Get the data from the form
        country = request.form.get('country', '') 
        text = request.form.get('review', '') 
        photo = request.files.get('photo', None)
        photo_filename = 'NULL'
        
        # Save the photo to the upload folder
        try:
            if photo:
                photo_filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        except:
            pass
            
        # Save the country name, review text, and photo filename to the database
        author = session.get('name', 'Anonymous')
        if(len(country)>0):
            review.add_review(country, text, photo_filename, author)
            flash('Successfully reviewed')
    # This function retrieves all the reviews from the database and sorts them based on the date they were created
    try:
        all_reviews = sorted(review.get_all_reviews(), key=lambda x: x['date'], reverse=True)
        return render_template('reviews.html', reviews=all_reviews)
    except:
        return render_template('reviews.html')
    

@app.route('/review/<int:review_id>/rate', methods=['POST'])
def rate_review(review_id):
    rating = int(request.form['rating'])
    review.add_rating(review_id, rating)
    flash('Rating added successfully!')
    return redirect(url_for('reviews'))


@app.route('/out')
def signout():
    session.clear()
    return redirect("/")



@app.route('/sign', methods=['POST'])
def check_user():
    form = request.form
    mail = form['email']
    password = form['pw']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, email, password FROM users WHERE email = %s", (mail,))
    user = cursor.fetchone()

    if user and hashlib.sha256(password.encode('utf-8')).hexdigest() == user['password']:
        session['user_id'] = user['id']
        session['name'] = user['email']
        session['ip_address'] = request.remote_addr
        session.permanent = True  # Set the session to be permanent (i.e. saved in a cookie)
        return redirect('/')
    else:
        flash('Invalid email or password')
    return redirect('/') 

@app.route('/change_list', methods=['GET', 'POST'])    
def change_list():
    if 'name' in session:
        try:
            list_of_travels = review.get_my_travels(session['name'])
            print(list_of_travels)
            return render_template('build_list.html',data=list_of_travels)
        except: ...
    return render_template('build_list.html')


@app.route('/question', methods=['GET', 'POST'])    
def question():
    try:
        all_questions = review.get_all_questions()
        return render_template('ask_others.html',all_questions=all_questions )    
    except:
        return render_template('ask_others.html') 
    
@app.route('/add_trip', methods=['POST'])
def add_trip():
    user_name = session['name']
    country = request.form['country']
    month_year = request.form['month_year']
    cities = request.form['cities']
    duration = request.form['duration']
    budget = request.form['budget']
    rating = request.form['rating']
    # Split month and year from month_year
    year, month = month_year.split('-')
    review.add_trip(user_name, country, month, year, cities, duration, budget, rating)
    return redirect('/change_list') 




@app.route('/new_question', methods=['POST'])    
def add_community_question():
    question = request.form.get('question', '')
    author_que = session.get('name', 'Anonymous')
    review.add_community_question(question,author_que)
    return redirect('/question')
    
 
    
@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    go to the main page
    '''
    if request.method == 'POST':
        if check_user():
            return render_template('index.html')
    #----test only----
    try:
        cursor = mysql.connection.cursor()
        result_value = cursor.execute("SELECT * FROM users;")
        if(result_value>0):
            users = cursor.fetchall()
            return render_template('index.html',users=users)
    except:
        ...
    return render_template('index.html')

def hash_password(password):
    """Returns the SHA-256 hash of the given password string."""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        name = form['username']
        email = form['mail']
        password = form['password']
        c_password = form['confirm_password']
        date_of_birth_str = request.form['date_of_birth']
        country = request.form['country']
        avatar = None  # You can add code to handle file uploads and save the path to the file here
        errors = []
        
        # Validate date of birth
        try:
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            if date_of_birth > date.today():
                raise ValueError('Date of birth must be in the past')
        except ValueError as e:
            errors.append(str(e))
            
        # Validate country code
        if len(country) != 2:
            errors.append('Invalid country code. Use two-letter country code.')
            
        # Validate email address
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            errors.append('Invalid email address')
            
        # Validate passwords match
        if password != c_password:
            errors.append('Passwords do not match')
            
        if not errors:
            # Hash the user's password
            hashed_password = hash_password(password)
            review.register_user(name, email, hashed_password, date_of_birth, country, avatar)
            return redirect('/')
        
        flash(errors)
        return redirect('/register')
        
    return render_template('register.html')

@app.route('/delete-photo/<filename>', methods=['POST'])
def delete_photo(filename):
    # code to delete photo from storage
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Photo deleted successfully!', 'success')
    else:
        flash('Failed to delete photo.', 'error')
    return redirect(url_for('photos'))

@app.route('/map')
def map_page():
    try:
        map = review.create_map()
        return render_template('map.html', map=map._repr_html_())
    except:
        return render_template('map.html')
    
@app.route('/photos')
def photos():
    photo_folder = 'static/uploads' # Set the path to your photo folder here
    photos = os.listdir(photo_folder)
    shuffle(photos) # Randomly sort the list of photos
    return render_template('photos.html', photos=photos)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(debug=True)
