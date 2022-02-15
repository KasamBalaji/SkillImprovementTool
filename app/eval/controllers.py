from flask import Blueprint,request,redirect,url_for,flash,render_template,jsonify,session
from flask.views import View
from flask_login import login_required 
eval = Blueprint('eval',__name__)

class Problem(View):
        decorators = [login_required]

        def dispatch_request(self):
            print("Logged In: ", session["user_id"])
            qno = request.form.get('qno')
            if qno:
                qno = int(qno)
            skills = request.args.get('skills')    
            if session.get("qno")is not None :
                if qno is not None and session.get("qno")==qno:
                    session["qno"] = qno+1
            elif skills is not None:
                print("Skills")
                session["qno"]=1
                # first time so load  qno, tasks into session
                #Get tasks for required skill
                session["task_ids"]=[1,2,3]

            #else flash and redirect
            else:
                flash("There is no previous session and Can't Start new session without any Skills")
                return redirect(url_for('index'))

            curr_q = session["qno"]
            task_id =session["task_ids"][curr_q-1]
            # task = #Query for task
            # session["task"]=task
            # question type
            qc="CQ"
            
            if qc=="CQ":
                content_labels= ["title","description","instructions","constraints","examples","referencelinks"] 
                session["task_data"]=task_content
                task_data = {key:task_content[key] for key in content_labels}
                return render_template('eval/CQ.html',task_data =task_data)


            return render_template('eval/CQ.html')
            

eval.add_url_rule('/temp',view_func=Problem.as_view('temp'))
eval.add_url_rule('/test',view_func=Problem.as_view('test'))

@login_required
@eval.route('/testcases',methods=['POST'])
def testcases():
    if request.method=='POST':
        code = request.get_json()
        print(code)
        results = {'rows': "Testcases got solved"}
        return results

