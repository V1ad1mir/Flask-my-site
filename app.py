from flask import Flask,render_template,request,session,redirect
from flask_mysqldb import MySQL
import yaml
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

#DB configuration
x = open('db.yaml')
db = yaml.safe_load(x)

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.urandom(24)


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

@app.route('/reviews')
def reviews():
    '''
    go to reviwes page
    '''
    return render_template('reviews.html')



if __name__ == '__main__':
    app.run(debug=True)
