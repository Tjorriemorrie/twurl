from src import app
from flask import request, render_template
from userModel import User


@app.route('/')
def index():
    params = {
        'user': User.getCurrentUser(),
    }
    app.logger.info('[Website] Index {}'.format(params))
    return render_template('website.html', **params)
