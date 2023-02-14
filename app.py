from flask import Flask,render_template,request,session,redirect,flash
from flask_mysqldb import MySQL
import yaml
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import review

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




@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        # Get the data from the form
        country = request.form['country'] 
        text = request.form['review'] 
        photo = request.files['photo'] 
        photo_filename = secure_filename(photo.filename) 
        
        # Save the photo to the upload folder
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)) 
        
        # Save the country name, review text, and photo filename to the database
        review.add_review(country, text, photo_filename)
        
    # This function retrieves all the reviews from the database
    all_reviews = review.get_all_reviews() 
    return render_template('reviews.html', reviews=all_reviews)

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
    
def check_user():
    form = request.form
    mail = form['email']
    password = form['pw']
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT * FROM users WHERE mail = %s AND password = %s", (mail,password) )
    if(result_value==1):
        session['username']=mail
        session['ip_address'] = request.remote_addr
        return True

@app.route('/change_list', methods=['GET', 'POST'])    
def change_list():
    return render_template('build_list.html')

@app.route('/question', methods=['GET', 'POST'])    
def question():
    return render_template('ask_others.html')
 
    
@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    go to the main page
    '''
    if request.method == 'POST':
        if check_user():
            return render_template('index.html') 
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT * FROM users;")
    if(result_value>0):
        users = cursor.fetchall()
        return render_template('index.html',users=users)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    go to the map page
    '''
    if request.method == 'POST':
        form = request.form
        name = form['username']
        mail = form['mail']
        password = form['password']
        c_password = form['confirm_password']
        if(password==c_password):
            #password = generate_password_hash(password)
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO users(name, mail, password) VALUES (%s, %s, %s)", (name,mail,password))
                mysql.connection.commit()
                print('OK')
            except:
                ...
    return render_template('register.html')

@app.route('/map')
def map_page():
    '''
    go to the map page
    '''
    return render_template('map.html')

@app.route('/photos')
def photos():
    '''
    go to photos page
    '''
    return render_template('photos.html')


if __name__ == '__main__':
    app.run(debug=True)
