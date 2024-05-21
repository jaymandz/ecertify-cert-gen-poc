from flask import Flask, render_template

application = Flask(__name__)

@application.get('/')
def index():
    return render_template('base.html')
