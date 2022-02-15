from flask import Blueprint,request,redirect,url_for,flash,render_template,jsonify,session
from flask.views import View
from flask_login import login_required 
from app.models import TaskSkill,Task
from app import db
from sqlalchemy import text
from app.eval.codechecker import codechecker
eval = Blueprint('eval',__name__)




@eval.route('/db')
def daba():
    skills = ["HTML","CSS"]
    tasks =db.session.query(TaskSkill).from_statement(text("SELECT * FROM task_skills WHERE CAST(skill_values->>'HTML' AS INTEGER)>=1000 and CAST(skill_values->>'CSS' AS INTEGER)>=1000")).all()
    print(tasks)
    session["qno"]=None
    return 'Hello'

class Problem(View):
        decorators = [login_required]

        def get_task_ids(self,skills):
            skills = ["HTML","CSS"]
            tasks =db.session.query(TaskSkill).from_statement(text("SELECT * FROM task_skills WHERE CAST(skill_values->>'HTML' AS INTEGER)>=1000 and CAST(skill_values->>'CSS' AS INTEGER)>=1000")).all()
            task_ids =[ task.task_id for task in tasks]
            return task_ids

        def dispatch_request(self):
            session["qno"]=None
            print("Logged In: ", session["user_id"])
            qno = request.form.get('qno')
            if qno:
                qno = int(qno)
            skills = request.args.get('skills') 


            if session.get("qno")is not None :
                if qno is not None and session.get("qno")==qno:
                    session["qno"] = qno+1
            elif skills is not None:
                session["qno"]=1
                session["task_ids"] = self.get_task_ids(skills)
                print(session["task_ids"])
            else:
                flash("There is no previous session and Can't Start new session without any Skills")
                return redirect(url_for('index'))

            curr_q = session["qno"]
            task_id =session["task_ids"][curr_q-1]
            task = Task.query.filter_by(id=4).first()
            print(task)
            qc=task.q_code
            print("qc is ",qc)
            if qc=="QC":
                content_labels= ["title","description","instructions","constraints","examples","referencelinks"] 
                session["task_data"]=task.task_content
                task_data = {key:task.task_content[key] for key in content_labels}
                return render_template('eval/CQ.html',task_data =task_data)


            return render_template('404.html')
            

eval.add_url_rule('/temp',view_func=Problem.as_view('temp'))
eval.add_url_rule('/test',view_func=Problem.as_view('test'))


def create_file(filename,content):
    text_file = open(filename,"w")
    text_file.write(content)
    text_file.close()

@login_required
@eval.route('/testcases',methods=['POST'])
def testcases():
    if request.method=='POST':
        code = request.get_json()
        print(code)
        #Creating Code File
        ext ="py"
        filename = "code."+ext
        create_file(filename,code)

        inputs=["1"]
        outputs=["2"]

        for input,output in zip(inputs,outputs):
            create_file("input.txt",input)
            create_file("output.txt",output)
        codechecker(filename, inputfile="input.txt", expectedoutput="output.txt", timeout=1, check=True)
        results = {'rows': "Testcases got solved"}
        return results

