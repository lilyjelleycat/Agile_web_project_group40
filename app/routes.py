from flask import render_template
from app import app, routes, models

@app.route('/')
def home():
    return render_template('intro.html')