from flask import Flask
from settings import SECRET_KEY
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from duckling import DucklingWrapper
from datetime import timedelta

duckling = DucklingWrapper()



app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = SECRET_KEY
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)


bcrypt = Bcrypt(app)
CORS(app)
db = SQLAlchemy(app)

from chatbot import routes
