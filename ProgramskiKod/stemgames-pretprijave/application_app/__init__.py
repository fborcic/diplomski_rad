from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.secret_key = 'jakotajnikljuc'
app.config.from_object(Config)
db = SQLAlchemy(app)

from .views import app_form
Bootstrap(app)
app.register_blueprint(app_form)
