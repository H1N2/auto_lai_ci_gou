from flask import render_template
from flask import Flask,url_for
app = Flask(__name__)

@app.route('/home/')
@app.route('/home/<name>')
def home(name=None):
    return render_template('home.html', name=name)

url_for('static', filename='style.css')