from sqlalchemy import false
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager   
from sqlalchemy.dialects.postgresql import JSON


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

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
    return User.query.get(int(user_id))

class Skill(db.Model):
    __tablename__='skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class UserSkill(db.Model):
    __tablename__='user_skills'
    id = db.Column(db.Integer, primary_key=True)
    skill_id= db.Column(db.Integer(), db.ForeignKey('skills.id'))
    user_id= db.Column(db.Integer(), db.ForeignKey('users.id'))
    value= db.Column(db.Float(),nullable=False)

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
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    value = db.Column(db.Float(),nullable=False)

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
    submission_id = db.Column(db.Integer(), db.ForeignKey('submissions.id'))
    updatedskillvalue = db.Column(JSON, nullable=False)

class UserSkillUpdate(db.Model):
    __tablename__='user_skill_updates'
    id = db.Column(db.Integer, primary_key=True)
    time_stamp = db.Column(db.DateTime, server_default=db.func.now())
    submission_id = db.Column(db.Integer(), db.ForeignKey('submissions.id'))
    updatedskillvalue = db.Column(JSON, nullable=False)






    
