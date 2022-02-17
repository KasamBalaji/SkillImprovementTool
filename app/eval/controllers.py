from flask import Blueprint,request,redirect,url_for,flash,render_template,jsonify,session
from flask.views import View
from flask_login import login_required 
from app.models import TaskSkill,Task,Batches,UserSkill,Submissions,TaskSkillUpdate
from app import db
from sqlalchemy import text
from sqlalchemy.sql import func
from app.eval.codechecker import codechecker,STATUS_CODES
from app.eval.forms import MCQForm
import os,random
eval = Blueprint('eval',__name__)




@eval.route('/db')
def daba():
    # skills = ["HTML","CSS"]
    # tasks =db.session.query(TaskSkill).from_statement(text("SELECT * FROM task_skills WHERE CAST(skill_values->>'HTML' AS INTEGER)>=1000 and CAST(skill_values->>'CSS' AS INTEGER)>=1000")).all()
    # print(tasks)
    # session["qno"]=None

    # res = db.session.query(func.avg(Batches.time),func.stddev_pop(Batches.time)).filter_by(user_id=1).first()
    # print(res)


    # task_id =1
    # user_id =1
    # result ={"answer":"TheAnswer"}
    # submission = Submissions(task_id=task_id,user_id=user_id,result=result)
    # db.session.add(submission)
    # db.session.commit()
    # db.session.flush()
    # sub_id = submission.id
    # batch_no=1
    # for i in range(10):
    #     quality = random.randint(1,101)
    #     time = random.randint(300,500)
    #     skillgaps = {'HTML': random.randint(500,700)}
    #     batch = Batches(batch_number=batch_no,user_id=user_id,task_id=task_id,submission_id=sub_id,quality=quality,time=time,skills=skillgaps)
    #     db.session.add(batch)
    #     db.session.commit()
    res=  db.engine.execute("SElECT percent_rank FROM  (SELECT time, PERCENT_RANK() OVER(order by time) FROM batches where task_id={}) pt where time={}".format(1,322)).fetchall()
    print(res[0][0])
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
                session["skills"]=skills
                print(session["task_ids"])
            else:
                flash("There is no previous session and Can't Start new session without any Skills")
                return redirect(url_for('index'))

            curr_q = session["qno"]
            task_id =session["task_ids"][curr_q-1]
            task = Task.query.filter_by(id=1).first()
            session["task_skills"]=task.skills.lower().split('||')
            session["task_e_code"]=task.e_code
            session["task_q_code"]=task.q_code
            session["task_data"]=task.task_content
            print(task)
            qc=task.q_code
            print("qc is ",qc)
            if qc=="qc1":
                content_labels= ["title","description","instructions","constraints","examples","referencelinks"] 
                task_data = {key:task.task_content[key] for key in content_labels}
                languages=[]
                if 'coding' in session["task_skills"]:
                    temp = ['python','java','cpp','c']
                    languages = [lang  for lang in temp if lang in session["skills"]]
                return render_template('eval/qc1.html',task_data =task_data,qno=session["qno"],languages=languages)
            
            if qc=='qc3':
                content_labels = ["content","options","relatedtags","referencelinks"]
                task_data = {key:task.task_content[key] for key in content_labels}
                task_data["options"]= task_data["options"].split('||')
                choices = [(i+1,choice) for i,choice in zip(range(len(task_data["options"])),task_data["options"])]
                form = MCQForm()
                form.set(choices)
                return render_template('eval/qc3.html',task_data=task_data,qno=session["qno"],form=form)
            
            if qc=='qc4':
                content_labels = ["content","relatedtags","referencelinks"]
                task_data = {key:task.task_content[key] for key in content_labels}
                return render_template('eval/qc4.html',task_data=task_data,qno=session["qno"])
                



            return render_template('404.html')
            

eval.add_url_rule('/temp',view_func=Problem.as_view('temp'))
eval.add_url_rule('/test',view_func=Problem.as_view('test'))


def create_submission(task_id,user_id,result):
    submission = Submissions(task_id=task_id,user_id=user_id,result=result)
    db.session.add(submission)
    db.session.commit()
    db.session.flush()
    return submission.id


def create_file(filename,content):
    text_file = open(filename,"w")
    text_file.write(content)
    text_file.close()

def update_skill_batch(user_id,task_id,sub_id,quality,time,type):
    #Get User Object
    user = User.query.filter_by(id=user_id).first()
    userskill = UserSkill.query.filter_by(user_id=user_id).first()
    user_skill_values = userskill.skill_values
    #Get Task Skills Object
    taskskill = TaskSkill.query.filter_by(task_id=task_id).first()
    task_skill_values = taskskill.skill_values

    #Get Skill Gaps for Skill in taskskill
    skillgaps ={}
    for skill in task_skill_values:
        skillgaps[skill]=task_skill_values[skill]-user_skill_values[skill]
    
    #Batch Number
    batch_no = user.batches_completed +1
    #Create a Batch
    batch = Batches(batch_number=batch_no,user_id=user_id,task_id=task_id,submission_id=sub_id,quality=quality,time=time,skills=skillgaps)
    db.session.add(batch)
    db.session.commit()

    #Get Score using percentile
    percentile=  db.engine.execute("SElECT percent_rank FROM  (SELECT time, PERCENT_RANK() OVER(order by time) FROM batches where task_id={}) pt where time={}".format(1,322)).fetchall()[0][0]
    percentile = 1- percentile
    score = quality*percentile
    #Update Skills

    user_skill_cnts = userskill.skillcnts
    task_cnt = taskskill.cnt

    task_k = 100/sqrt(1+task_cnt)

    for skill in task_skill_values:
        t_rating = task_skill_values[skill]
        u_rating = user_skill_values[skill]
        user_k = 100/sqrt(1+ user_skill_cnts[skill])
        exp = t_rating- u_rating
        expected_score =  1/((10.0**(exp))+1)

        if task_cnt>=50 or type=='gtype':
            user_skill_values[skill] = u_rating + user_k*(score- expected_score)
            user_skill_cnts[skill] +=1
            
        
        if type!='gtype':
            task_skill_values[skill] = t_rating - task_k*(score-expected_score)
    
    if type!='gtype':
        task_cnt +=1

    userskill.skill_values = user_skill_values
    userskill.skillcnts = user_skill_cnts

    taskskill.cnt = task_cnt
    taskskill.skill_values = task_skill_values

    db.session.add(userskill)
    db.session.add(taskskill)
    db.session.commit()
        

            



    #Update Skill based on type
    # for skill in task_skill_values:






    



@login_required
@eval.route('/submit',methods=['POST'])
def submit():
    if request.method=='POST':
        data = request.get_json()
        type = data["type"]
        qno = int(data["qno"])
        # time = data["time"]

        q_code = session["task_q_code"]
        e_code = session["task_e_code"]
        task_id = session["task_ids"][qno-1]
        user_id = session["user_id"]
        
        print(q_code)
        print(e_code)
        
        if q_code=='qc1':
            if e_code=='ec1':
                total = 1
                if type=='test':
                    total = 0.1
                code = data["code"]
                print(code)
                #Creating Code File
                ext ="py"
                filename = "usercode."+ext
                create_file(filename,code)
                inputs = session["task_data"]["testcasesinput"]
                outputs = session["task_data"]["testcasesoutput"]
                inputs = inputs[:len(inputs)*total]
                outputs = outputs[:len(outputs)*total]
                passed =0
                for input,output in zip(inputs,outputs):
                    create_file("input.txt",input)
                    create_file("eoutput.txt",output+"\n")
                    code,result =codechecker(filename, inputfile="input.txt", expectedoutput="eoutput.txt", timeout=1, check=True)
                    if code==201:
                        passed +=1
                    os.remove("input.txt")
                    os.remove("output.txt")
                    os.remove("eoutput.txt")
                flash(f"{cnt}/{len(inputs)} Testcases got solved")
                if type=='test':    
                    results = {'result': f"{cnt}/{len(inputs)} Testcases got solved"}
                    return results
                quality = cnt/len(inputs)
                time = 500
                result = {"answer":code}
                sub_id =create_submission(task_id,user_id,result)
                update_skill_batch(user_id,task_id,sub_id,quality,time,type)

                
                
        
        if q_code=='qc3':
            print(data)
            if e_code=='ec4':
                answer = data["answer"].lower()
                if (answer == session["task_data"]["answer"].lower()):
                    quality =1
                else:
                    quality =0
                time = 500
                print(quality)
                result = {"answer":answer}
                sub_id =create_submission(task_id,user_id,result)
                update_skill_batch(user_id,task_id,sub_id,quality,time,type)
        
        if q_code=='qc4':
            print(data)
            if e_code=='ec4':
                answer = data["answer"].lower()
                if( answer == session["task_data"]["answer"].lower()):
                    quality=1
                else:
                    quality=0
                time = 500
                print(quality)
                result = {"answer":answer}
                sub_id =create_submission(task_id,user_id,result)
                update_skill_batch(user_id,task_id,sub_id,quality,time,type)




        results = {'result': f"Dummy Message"}
        return results        


