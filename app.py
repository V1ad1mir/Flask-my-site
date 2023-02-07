from flask import Flask,render_template,request


app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def index():
    # if request.method == 'POST':
    #     return request.form['password']
    return render_template('index.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/photos')
def photos():
    return render_template('photos.html')

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')



if __name__ == '__main__':
    app.run(debug=True)
