# Import the Flask Framework
from flask import Flask
from flask.ext.cors import CORS


app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


# enable cors
CORS(app)


# configuration
app.config.from_pyfile('config.py')

# import views
import views
