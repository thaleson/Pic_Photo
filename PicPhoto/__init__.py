from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)

# Certifique-se de que a variável de ambiente DATA_BASEURL está definida
DATABASE_URL = "postgresql://database_url_h0r0_user:kgfYYZBU3ELi8BaZWkcNmQqdV5wjfkWI@dpg-cpg4k30l5elc738n8js0-a/database_url_h0r0"
if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATA_BASEURL não está definida")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "7d443106a96cfc3c4cf728ca949a3498")
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "static/photos_posts")

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = "homepage"

# Importar as rotas depois da inicialização dos componentes acima
from PicPhoto import routes
