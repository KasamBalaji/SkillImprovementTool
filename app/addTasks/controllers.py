from audioop import add
from flask import Blueprint
from flask import Flask, render_template, request, jsonify

from flask import render_template, redirect, request, url_for
from app.addTasks.forms import FillInTheBlanksTypeQuestionForm

from app.models import User,Skill,UserSkill,Task,TaskSkill,Submissions,TaskSkillUpdate, UserSkillUpdate
from app import db


addTasks = Blueprint('addTasks', __name__)


@addTasks.route('/', methods=['POST', 'GET'])
def index():
    task_content = {}
    if request.method == 'POST':
        task_content = request.form['content']
    return render_template('addTasks/index.html', tasks=task_content)


@addTasks.route('/addQuestions', methods=['POST', 'GET'])
def addQuestions():
    if request.method == 'POST':
        return render_template('addTasks/index.html')
    else:
        return render_template('addTasks/addingQuestions.html')


@addTasks.route('/addingEssay',methods=['POST','GET'])
def addingEssay():
    if request.method =='POST':
        tasks =request.form
        content = tasks["content"] 
        relatedtags = tasks["relatedtags"]
        answer = tasks["criterias"] 
        links = tasks["links"] 
        skills =""
        skill_list=['C++','JAVA','PYTHON','OOPS','HTML','CSS','JAVASCRIPT']
        for skill in skill_list:
            if request.form.get(skill):
                skills=skills+skill+"||" 
        skills = skills[:-2]
        task_content = jsonify(
            skills=skills,
            content=content, 
            relatedtags=relatedtags,
            answer=answer,
            referencelinks=links,
        )
        print(task_content.data)
        task = Task(task_content={
                "content" : content, 
                "relatedtags" : relatedtags,
                "answer" : answer,
                "referencelinks" : links,
        },
                    skills=skills,
                    tags=relatedtags,
                    q_code='qc5',
                    e_code='ce')
        db.session.add(task)
        db.session.commit()
        return render_template('addTasks/index.html', tasks=tasks)

    else:
        return render_template('addTasks/addingEssayType.html')



@addTasks.route('/addingFillInTheBlanks', methods=['POST', 'GET'])
def addingFillInTheBlanks():
    if request.method == 'POST':
        tasks = request.form
        content = tasks["content"] 
        relatedtags = tasks["relatedtags"]
        answer = tasks["answer"] 
        links = tasks["links"] 
        skills =""
        skill_list=['C++','JAVA','PYTHON','OOPS','HTML','CSS','JAVASCRIPT']
        for skill in skill_list:
            if request.form.get(skill):
                skills=skills+skill+"||" 
        skills = skills[:-2]
        task_content = jsonify(
            skills=skills,
            content=content, 
            relatedtags=relatedtags,
            answer=answer,
            referencelinks=links,
        )
        print(task_content.data)
        task = Task(task_content={
                "content" : content, 
                "relatedtags" : relatedtags,
                "answer" : answer,
                "referencelinks" : links,
        },
                    skills=skills,
                    tags=relatedtags,
                    q_code='qc4',
                    e_code='ec4')
        db.session.add(task)
        db.session.commit()
        return render_template('addTasks/index.html', tasks=tasks)
    else: 
        return render_template('addTasks/addingFillInTheBlanksTypeQuestion.html')


@addTasks.route('/addingMUltipleChoiceQuestion', methods=['POST', 'GET'])
def addingMUltipleChoiceQuestion():
    if request.method == 'POST':
        tasks = request.form
        content = tasks["content"]
        options = tasks["options"]
        relatedtags = tasks["relatedtags"]
        answer = tasks["answer"] 
        links = tasks["links"]
        skills =""
        skill_list=['C++','JAVA','PYTHON','OOPS','HTML','CSS','JAVASCRIPT']
        for skill in skill_list:
            if request.form.get(skill):
                skills=skills+skill+"||" 
        skills = skills[:-2]

        task_content = jsonify(
            content=content,
            options=options,
            relatedtags=relatedtags,
            answer=answer,
            referencelinks=links,
        )
        print(task_content.data)
        task = Task(task_content={
                "content" : content,
                "options" : options,
                "relatedtags" : relatedtags,
                "answer" : answer,
                "referencelinks" : links,
        },
                    skills=skills,
                    tags=relatedtags,
                    q_code='qc3',
                    e_code='ec3')
        db.session.add(task)
        db.session.commit()
        return render_template('addTasks/index.html', tasks=tasks)
    else:
        return render_template('addTasks/addingMCQTypeQuestion.html')


@addTasks.route('/addingCodingQuestion', methods=['POST', 'GET'])
def addingCodingQuestion():
    if request.method == 'POST':

        tasks = request.form
        title = tasks["title"]
        description = tasks["description"]
        instructions = tasks["instructions"]
        constraints = tasks["constraints"]
        examples = tasks["examples"]
        solutionlanguage = tasks["solutionlanguage"]
        answer = tasks["answer"]
        links = tasks["referencelinks"]
        relatedtags = tasks["relatedtags"] 
        testCaseInput= tasks["input"]
        testCaseOutput =  tasks["output"]   

        task = Task(task_content={
                "title" : title,
                "description" : description, 
                "instructions" : instructions,
                "constraints" : constraints,
                "examples" : examples,
                "solutionlanguage" : solutionlanguage,
                "answer" : answer,
                "referencelinks" : links,
                "testcasesinput" : [testCaseInput],
                "testcasesoutput" : [testCaseOutput]
        },
                    skills="coding",
                    tags=relatedtags,
                    q_code='qc1',
                    e_code='ec1')
        print(testCaseInput)
        print(testCaseOutput) 
        db.session.add(task)
        db.session.commit()
        return render_template('addTasks/index.html', tasks=tasks)
    else:
        return render_template('addTasks/addingCodingTypeQuestion.html')
