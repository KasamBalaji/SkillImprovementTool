from flask import Flask,render_template,redirect,url_for,session,flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_required
from app.forms import SkillForm 



app = Flask(__name__)
app.config.from_object('config')
app.secret_key = "abc"

db = SQLAlchemy(app)
bootstrap =Bootstrap(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from app.auth.controllers import auth
from app.eval.controllers import eval
from app.addTasks.controllers import addTasks
app.register_blueprint(auth,url_prefix='/auth')
app.register_blueprint(eval,url_prefix='')
app.register_blueprint(addTasks, url_prefix='/addTasks')



@app.route('/',methods=['GET','POST'])
@login_required
def index():
    session["qno"]=None
    form = SkillForm()
    if form.validate_on_submit():
        if form.submit1.data:
            return redirect(url_for('eval.temp',skills=form.skills.data))
        elif form.submit2.data:
            return redirect(url_for('eval.test',skills=form.skills.data))
    return render_template('index.html',form=form)
    


@app.route('/ratings',methods=['GET'])
def getratings():
    user_id = session["user_id"]
    skill =db.engine.execute(f'SELECT skill_values from user_skills where user_id={user_id}').fetchone()[0]

    return render_template('ratings.html',skill=skill)