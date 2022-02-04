from flask import Flask

app = Flask(__name__)
app.config.from_object('config')


from app.auth.controllers import auth_bp
app.register_blueprint(auth_bp,url_prefix="")


