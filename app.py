from flask import Flask,render_template,request,session,redirect,flash, url_for
from flask_mysqldb import MySQL
import yaml
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import review
import re

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


@app.route('/sign', methods=['GET', 'POST'])
def check_user():
    form = request.form
    mail = form['email']
    password = form['pw']
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (mail,password) )

    if(result_value==1):
        cursor.execute("SELECT username FROM users WHERE email = %s", (mail,))
        result = cursor.fetchone()
   
        session['email']=mail
        session['name']=result['username']
        session['ip_address'] = request.remote_addr
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    go to the map page
    '''
    if request.method == 'POST':
        form = request.form
        name = form['username']
        email = form['mail']
        password = form['password']
        c_password = form['confirm_password']
        date_of_birth = request.form['date_of_birth']
        country = request.form['country']
        avatar = None  # You can add code to handle file uploads and save the path to the file here
        errors = []
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            errors.append("Invalid email address")
        if(password!=c_password):
            errors.append("Passwords not equals")
        if not errors:
            #password = generate_password_hash(password)
            try:
                print(name, email, password,date_of_birth,country,avatar)
                review.register_user(name, email, password,date_of_birth,country,avatar)
                return redirect('/')
            except:
                ...
    return render_template('register.html')

@app.route('/map')
def map_page():
    '''
    go to the map page
    '''
    # create the map
    try:
        map = review.create_map()
        return render_template('map.html', map=map._repr_html_())
    except:
        return render_template('map.html')
    

@app.route('/photos')
def photos():
    '''
    go to photos page
    '''
    return render_template('photos.html')


if __name__ == '__main__':
    app.run(debug=True)
