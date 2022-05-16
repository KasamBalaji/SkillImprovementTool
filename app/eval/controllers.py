from flask import Blueprint,request,redirect,url_for,flash,render_template,jsonify,session
from flask.views import View
from flask_login import login_required 
from app.models import TaskSkill,Task,Batches,UserSkill,Submissions,TaskSkillUpdate
from app import db
from sqlalchemy import text
from sqlalchemy.sql import func
from app.eval.codechecker import codechecker,STATUS_CODES
from app.eval.forms import MCQForm
import os,random,itertools,math
from scipy.stats import skewnorm
from collections import OrderedDict
import datetime,time
eval = Blueprint('eval',__name__)


sqls ={
    "OB_PF": "SELECT avg(quality) ,avg(time) ,avg(CAST(skill_gaps->>'{skill}' AS INTEGER)) FROM batches \
WHERE batch_number= (SELECT batch_number FROM batches WHERE user_id={user_id} ORDER BY batch_number DESC LIMIT 1) \
AND skill_gaps->>'{skill}' IS NOT NULL",
"EXP_PF": "SELECT avg(quality), avg(time) FROM batches WHERE user_id={user_id} AND CAST(skill_gaps->>'{skill}' AS INTEGER) BETWEEN {lower} AND {upper}"
}

@eval.route('/db')
def daba():
    d = datetime.datetime.utcnow()
    start_date = int((d - datetime.datetime(1970, 1, 1)).total_seconds()*1000)
    return render_template('eval/base_type.html',start_date=start_date)
  

class Problem(View):
        decorators = [login_required]

        def get_performance_factors(self,skills,user_id):
            pfs = {}
            for skill in skills:
                obs_sql = sqls["OB_PF"].format(skill=skill,user_id=user_id)
                ob =db.engine.execute(obs_sql).fetchone()
                if ob[2] is not None:
                    exp_sql = sqls["EXP_PF"].format(skill=skill,user_id=user_id,lower=ob[2]-100,upper=ob[2]+100)
                    exp = db.engine.execute(exp_sql).fetchone()
                    d = math.sqrt((exp[0]-ob[0])**2 + (exp[1]-ob[1])**2)
                    s = math.erf(d)
                    pfs[skill]=s
            return pfs

        def get_task_ids(self,skills):
            return [1,2,3,4,5,6],""
            k=500
            userskill = UserSkill.query.filter_by(user_id=session["user_id"]).first()
            errors = []

            #Creating Queries for each skill
            queries = {}
            for skill in skills:
                if userskill.skill_values.get(skill) is None:
                    errors.append(skill)
                    continue
                skillvalue = userskill.skill_values[skill]
                queries[skill] = f"CAST(skill_values->>'{skill}' AS INTEGER) BETWEEN {skillvalue-k} AND {skillvalue+k}"
            
            if len(errors)>=0:
                return -1, "No skills for "+str(errors)
            
            #Getting tasks for given skill in a range
            task_ids = []
            for length in range(1,len(skills)+1):
                st = "SELECT * FROM task_skills WHERE "
                ed = f" length ={length}"
                combos = list(itertools.combinations(skills,length))
                for combo in combos:
                    sql = st
                    for skill in combo:
                        sql += queries[skill]+ " AND "
                    sql +=ed
                    res = db.engine.execute(sql).fetchall()
                    res =list(itertools.chain(*res))
                    task_ids.extend(res)
            
            #Getting Performance Factors
            Pfs = self.get_performance_factors(skills,session["user_id"])

            #Getting Learning Potential
            skill_values={}
            task_values ={}
            for task_id in task_ids:
                    query = f"SELECT skill_values FROM task_skills where task_id={task_id}"
                    values =db.engine.execute(query).fetchone()[0]
                    task_values[task_id]=values
            userskill = UserSkill.query.filter_by(user_id=session["user_id"]).first() 
            skillgaps ={}
            for task in task_values.values():
                for skill in task:
                    if skillgaps.get(skill) is None:
                        skillgaps[skill]=[]
                    skillgaps[skill].append(task[skill] - userskill.skill_values[skill])

            means ={}
            sds ={}
            for skill in skillgaps:
                mean = sum(skillgaps[skill]) / len(skillgaps[skill])
                variance = sum([((x - mean) ** 2) for x in skillgaps[skill]]) / len(skillgaps[skill])
                sd = variance ** 0.5
                means[skill]=mean
                sds[skill]=sd
            learning_potentials = {}
            for task_id in task_values:
                lp =0
                for skill in task_values[task_id]:
                    z = (task_values[task_id][skill] - means[skill])/sds[skill]
                    lp +=skewnorm.pdf(z,pfs[skill])
                learning_potentials[task_id]=lp
            
            sorted_taskids =dict(sorted(learning_potentials.items(),key=lambda item: item[1]))
            sorted_taskids = OrderedDict(reversed(list(sorted_taskids.items())))
            res = list(sorted_taskids.keys())
            #Selecting Top 10 Tasks
            res = res[:min(10,len(res))]
            return res ,""            
                    


        def get_type(self):
            return 'ltype'
            

        def dispatch_request(self):
            print("Logged In: ", session["user_id"], "Qno is ",session["qno"])

            ##Assigning Next Question or get Tasks for new batch
            qno = request.args.get('qno')
            print(request.args)
            if qno:
                qno = int(qno)
                print("qno from prev question: ",qno)
            skills = request.args.get('skills') 

            if session.get("qno")is not None :
                if qno is not None and session.get("qno")==qno:
                    session["qno"] = qno+1
                    d = datetime.datetime.utcnow()
                    start_date = int((d - datetime.datetime(1970, 1, 1)).total_seconds()*1000)
                    session["start_date"]=start_date

            elif skills is not None:
                session["task_ids"],err = self.get_task_ids(skills)
                if(session["task_ids"]==-1):
                    flash(err)
                    return redirect(url_for('index'))
                session["qno"]=1
                session["skills"]=skills
                d = datetime.datetime.utcnow()
                start_date = int((d - datetime.datetime(1970, 1, 1)).total_seconds()*1000)
                session["start_date"]=start_date
                print(session["task_ids"],session["qno"])
            else:
                flash("There is no previous session and Can't Start new session without any Skills")
                return redirect(url_for('index'))

            curr_q = session["qno"]
            #Batch Completed
            if(curr_q>=len(session["task_ids"])):
                flash("Batch Completed")
                return redirect(url_for('index'))
            
            ##Updating Task Details to Session
            task_id =session["task_ids"][curr_q-1]
            task = Task.query.filter_by(id=task_id).first()
            session["task_skills"]=task.skills.lower().split('||')
            session["task_e_code"]=task.e_code
            session["task_q_code"]=task.q_code
            session["task_data"]=task.task_content
            session["type"]=self.get_type()
            
            print(task)
            qc=task.q_code

            ##Rendering Based On Question Code
            print("qc is ",qc)
            if qc=="qc1":
                content_labels= ["title","description","instructions","constraints","examples","referencelinks"] 
                task_data = {key:task.task_content[key] for key in content_labels}
                languages=[]
                if 'coding' in session["task_skills"]:
                    temp = ['python','java','cpp','c']
                    languages = [lang  for lang in temp if lang in session["skills"]]
                return render_template('eval/qc1.html',task_data =task_data,qno=session["qno"],languages=languages,start_date=session["start_date"],type=session["type"])
            
            if qc=='qc3':
                content_labels = ["content","options","relatedtags","referencelinks"]
                task_data = {key:task.task_content[key] for key in content_labels}
                task_data["options"]= task_data["options"].split('||')
                choices = [(i+1,choice) for i,choice in zip(range(len(task_data["options"])),task_data["options"])]
                form = MCQForm()
                form.set(choices)
                return render_template('eval/qc3.html',task_data=task_data,qno=session["qno"],form=form,start_date=session['start_date'],type=session["type"])
            
            if qc=='qc4':
                content_labels = ["content","relatedtags","referencelinks"]
                task_data = {key:task.task_content[key] for key in content_labels}
                return render_template('eval/qc4.html',task_data=task_data,qno=session["qno"],start_date=session['start_date'],type=session["type"])
                



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
    return
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

    user_skill_cnts = userskill.skill_cnts
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
    userskill.skill_cnts = user_skill_cnts

    taskskill.cnt = task_cnt
    taskskill.skill_values = task_skill_values

    db.session.add(userskill)
    db.session.add(taskskill)
    db.session.commit()
        

            





    



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


