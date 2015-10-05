# Import the Flask Framework
from flask import Flask
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

# configuration
app.config.from_pyfile('config.py')

# import views
import views
