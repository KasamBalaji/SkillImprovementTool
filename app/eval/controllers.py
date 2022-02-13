from flask import Blueprint,request,redirect,url_for,flash,render_template,jsonify,session
from flask.views import View
from flask_login import login_required 
eval = Blueprint('eval',__name__)

class Problem(View):
        decorators = [login_required]

        def dispatch_request(self):
            skills = request.args.get('skills')
            if skills is None:
                flash("Can't Start without any Skills")
                return redirect(url_for('index'))
            return render_template('eval/codingq.html')


@eval.route('/test',methods=['GET','POST'])
@login_required
def test():
    qno = request.form.get('qno')
    skills = request.args.get('skills')
    if skills is None and session.get("qno") is None:
        flash("Can't Start without any Skills")
        return redirect(url_for('index'))
    if session.get("qno") is None:
        session["qno"]=1
    if qno is not None:
        qno = int(qno)
        # print("Qno is not None")
        print(session.get("qno"), "From session")
        if session.get("qno")==qno:
            # print("It is equal")
            session["qno"] = qno+1
            print(session["qno"], type(session["qno"]))
            return render_template('eval/codingq.html',qno=session["qno"])
    
    #code to get tasks, and display qno task

    return render_template('eval/codingq.html',qno=session.get("qno"))

eval.add_url_rule('/temp',view_func=Problem.as_view('temp'))

@login_required
@eval.route('/testcases',methods=['POST'])
def testcases():
    if request.method=='POST':
        code = request.get_json()
        print(code)
        results = {'rows': "Testcases got solved"}
        return results

