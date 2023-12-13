import os
from flask_cors import CORS
from flask import Flask, request
from flask_image_alchemy.storages import S3Storage
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from os.path import join, dirname, realpath
from flask_login import LoginManager


app = Flask(__name__)
CORS(app)
UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads/')

storage = S3Storage()
storage.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///internet_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOADS_PATH
app.config['MAX_CONTENT_LENGHT'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)