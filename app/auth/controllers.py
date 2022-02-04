from flask import Blueprint,render_template

auth_bp = Blueprint('auth',__name__)

@auth_bp.route('/')
def login():
    return render_template('auth/signin.html')
