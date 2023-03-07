from flask import Flask,render_template,request,session,redirect,flash, url_for
from flask_mysqldb import MySQL
import yaml
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import review
import server_operations
from datetime import datetime, date
from random import shuffle
import hashlib

from mysql.connector import Error

app = Flask(__name__)

#DB configuration
with open('db.yaml') as f:
    db = yaml.safe_load(f)

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


def is_valid_image(photo)->bool:
    """
    Checks whether a file is a valid image file.

    Parameters:
        photo (werkzeug.datastructures.FileStorage): The file to check.

    Returns:
        bool: True if the file is a valid image file, False otherwise.
    """
    if not photo:
        return False  # no file was provided
    
    # check if the file has an allowed image extension
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    if not '.' in photo.filename or photo.filename.split('.')[-1].lower() not in allowed_extensions:
        return False  # invalid extension
    
    # check if the file size is not larger than 2MB
    max_size_bytes = 2 * 1024 * 1024  # 2MB
    if photo.content_length > max_size_bytes:
        return False  # file too large
    
    return True  # the file is valid

def generate_sorting_dropdown(selected_sort_option=None):
    options = [
        ('', 'Select sort option'),
        ('date_asc', 'Date (oldest first)'),
        ('date_desc', 'Date (newest first)'),
        ('name_asc', 'Name (A-Z)'),
        ('name_desc', 'Name (Z-A)'),
    ]
    html = '<label for="sort_by">Sort by:</label>'
    html += '<select name="sort_by" onchange="this.form.submit()">'
    for value, label in options:
        selected = 'selected' if value == selected_sort_option else ''
        html += f'<option value="{value}" {selected}>{label}</option>'
    html += '</select>'
    return html


def generate_filtering_input(country_filter=None):
    html = '<label for="country_filter">Filter by country:</label>'
    html += f'<input type="text" name="country_filter" value="{country_filter}" placeholder="Enter country name">'
    html += '<button type="submit">Filter</button>'
    return html



@app.route('/admin')
def admin_page():
    #reviews, , trips, users = review.get_all_data()
    users = server_operations.get_all_users()
    community_questions = server_operations.get_all_community_questions()
    reviews = server_operations.get_all_reviews()
    travels = server_operations.get_my_travels('admin')
    return render_template('admin.html',users=users,questions=community_questions,posts=reviews,travels=travels)
    

@app.route('/query', methods=['POST'])
def query_results():
    query = request.form['query']
    try:
        server_operations.make_query(query)
    except:
        print('error')
    return render_template('admin.html',)



@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    """
    View function for the /reviews route.

    If a POST request is received, retrieves the country name, review text, and photo
    from the submitted form, saves the photo to the UPLOAD_FOLDER, and adds a new
    review to the database.

    Retrieves all the reviews from the database and sorts them based on the sort option
    specified in the request args. If a country filter is also specified, filters the
    reviews by the country. Renders the 'reviews.html' template and passes the reviews
    data to it.

    Returns:
        A Flask response object containing the rendered template or an error message.
    """

    # Handle form submission for adding a new review
    if request.method == 'POST':
        # Get the data from the form
        country = request.form.get('country', '')
        text = request.form.get('review', '')
        photo = request.files.get('photo', None)

        # Validate the input
        if photo and not is_valid_image(photo):
            flash('Invalid image file')
            return redirect(request.url)

        # Save the photo to the upload folder
        photo_filename = None
        if photo:
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        # Save the review to the database
        author = session.get('name', 'Anonymous')
        review.add_review(country, text, photo_filename, author)
        flash('Successfully reviewed')
        return redirect(request.url)

    # Retrieve reviews from the database and sort/filter them
    sort_option = request.args.get('sort_by', '')
    country_filter = request.args.get('country_filter', '')

    all_reviews = server_operations.get_all_reviews()
    
    if request.method == 'GET':
        if sort_option == 'date_asc':
            all_reviews.sort(key=lambda x: x['date'])
        elif sort_option == 'date_desc':
            all_reviews.sort(key=lambda x: x['date'], reverse=True)
        elif sort_option == 'name_asc':
            all_reviews.sort(key=lambda x: x['country'])
        elif sort_option == 'name_desc':
            all_reviews.sort(key=lambda x: x['country'], reverse=True)

        if country_filter != 'None':
            all_reviews = [r for r in all_reviews if r['country'].lower().startswith(country_filter.lower())]
            
    return render_template('reviews.html', reviews=all_reviews)

    

@app.route('/review/<int:review_id>/rate', methods=['POST'])
def rate_review(review_id):
    rating = int(request.form['rating'])
    review.update_rating(review_id, rating)
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
            list_of_travels = server_operations.get_my_travels(session['name'])
            print(list_of_travels)
            return render_template('build_list.html',data=list_of_travels)
        except: ...
    return render_template('build_list.html')


@app.route('/question', methods=['GET', 'POST'])    
def question():
    try:
        all_questions_list = server_operations.get_all_community_questions()
        
        # Check if the "Show questions with answers only" checkbox is checked
        checkbox_answers = request.args.get('answered', False, type=bool)
        
        # Filter the questions based on the checkbox value
        filtered_questions_list = all_questions_list if not checkbox_answers else [q for q in all_questions_list if q['answer'] is not None]
        
        return render_template('ask_others.html', all_questions=filtered_questions_list, show_answered_questions=checkbox_answers)    
    except Exception as e:
        flash('An error occurred: {}'.format(str(e)), 'error')
        return render_template('ask_others.html')
    
@app.route('/add_answer', methods=['POST'])
def add_answer():
    """
    Adds an answer to a question and redirects to the question page.

    The answer is obtained from the 'answer' field in the POST request.
    The author of the answer is obtained from the session.
    The ID of the question is obtained from the 'question_id' field in the POST request.
    The answer is saved using the 'set_answer_for_question' function from the 'review' module.

    Returns:
        A redirect to the 'question' function.
    """
    author_of_answer = session.get('name', 'Anonymous')
    question_id = request.form.get('question_id')
    answer = request.form.get('answer')
    review.set_answer_for_question(question_id, author_of_answer, answer)
    return redirect(url_for('question'))
    
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
    Go to the main page.
    '''
    return render_template('index.html')


def hash_password(password):
    """Returns the SHA-256 hash of the given password string."""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user based on submitted form data.

    Validates form inputs for user registration, including name, email,
    password, date of birth, country code, and password confirmation. If all
    inputs are valid, the user's password is hashed and saved to the database,
    and the user is redirected to the home page. Otherwise, the form is
    redisplayed with error messages.

    Returns:
        Rendered HTML template for user registration.
    """
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
        if not review.correct_mail_address(email):
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
    """
    This function deletes a photo with a given filename from the application's storage. 
    It first checks if the file exists in the upload folder, and if it does, it removes it from the folder. 
    It then displays a success or error message using Flask's flash() function and redirects the user to the photos page.

    Args:
        filename: str - the name of the file to be deleted
    Returns:
        redirect to the photos page
    """
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Photo deleted successfully!', 'success')
    else:
        flash('Failed to delete photo.', 'error')
    return redirect(url_for('photos'))

@app.route('/map')
def map_page():
    try:
        map_html = review.create_map()._repr_html_()
    except Exception as e:
        # Handle exceptions more gracefully
        map_html = None
        app.logger.error(f"Error creating map: {e}")
    return render_template('map.html', map=map_html)
    
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
