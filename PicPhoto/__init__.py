from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import  LoginManager
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("databaseurl")
app.config["SECRET_KEY"]="7d443106a96cfc3c4cf728ca949a3498"
app.config["UPLOAD_FOLDER"]="static/photos_posts"

database = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)

login_manager.login_view="homepage"

# Certifique-se de que a importação das rotas está no final para evitar importações circulares
from PicPhoto import routes
