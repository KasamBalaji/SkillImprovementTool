from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
bootstrap =Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from app.auth.controllers import auth
app.register_blueprint(auth,url_prefix='/auth')


