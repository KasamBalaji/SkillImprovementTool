from sqlalchemy import false
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager   
from sqlalchemy.dialects.postgresql import JSON
<<<<<<< HEAD
from flask import session
=======
>>>>>>> origin/newbranch1


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
<<<<<<< HEAD
    batches_completed = db.Column(db.Integer)
=======
>>>>>>> origin/newbranch1

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        print(password)
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    session["user_id"]=user_id
    return user

class Skill(db.Model):
    __tablename__='skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class UserSkill(db.Model):
    __tablename__='user_skills'
    id = db.Column(db.Integer, primary_key=True) 
    user_id= db.Column(db.Integer(), db.ForeignKey('users.id'))
    skill_values = db.Column(JSON, nullable=false)

class Task(db.Model):
    __tablename__='tasks'
    id = db.Column(db.Integer, primary_key=True)
    task_content = db.Column(JSON)
    skills = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(50), nullable=False)
    q_code = db.Column(db.String(50), nullable=False)
    e_code = db.Column(db.String(50), nullable=False)

class TaskSkill(db.Model):
    __tablename__='task_skills'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    skill_values = db.Column(JSON, nullable=false)

class Submissions(db.Model):
    __tablename__='submissions'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer(), db.ForeignKey('tasks.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    result = db.Column(JSON, nullable=False)
    time_stamp = db.Column(db.DateTime, server_default=db.func.now())

class TaskSkillUpdate(db.Model):
    __tablename__='task_skill_updates'
    id = db.Column(db.Integer, primary_key=True)
    time_stamp = db.Column(db.DateTime, server_default=db.func.now())
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    updatedskillvalue = db.Column(JSON, nullable=False)

class UserSkillUpdate(db.Model):
    __tablename__='user_skill_updates'
    id = db.Column(db.Integer, primary_key=True)
    time_stamp = db.Column(db.DateTime, server_default=db.func.now())
    submission_id = db.Column(db.Integer(), db.ForeignKey('submissions.id'))
    updatedskillvalue = db.Column(JSON, nullable=False)

class Batches(db.Model):
    __tablename__='batches'
    id = db.Column(db.Integer, primary_key=True)
    batch_number = db.Column(db.Integer,nullable= False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    quality= db.Column(db.Float)
    time = db.Column(db.Float)
    skills = db.Column(JSON, nullable=False)




    
