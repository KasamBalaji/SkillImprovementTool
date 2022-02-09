from audioop import add
from flask import Blueprint
from flask import Flask, render_template, request, jsonify

from flask import render_template, redirect, request, url_for
from app.addTasks.forms import FillInTheBlanksTypeQuestionForm


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


@addTasks.route('/addingFillInTheBlanks', methods=['POST', 'GET'])
def addingFillInTheBlanks():
    # if request.method == 'POST':
    #     tasks = request.form
    #     content = tasks["content"]
    #     relatedtags = tasks["relatedtags"].split("||")
    #     answer = tasks["answer"].split("||")
    #     links = tasks["links"].split("||")

    #     task_content = jsonify(
    #         content=content,
    #         relatedtags=relatedtags,
    #         answer=answer,
    #         referencelinks=links,
    #     )
    #     print(task_content.data)

    #     return render_template('addTasks/index.html', tasks=tasks)
    # else:
    form=FillInTheBlanksTypeQuestionForm()
    if form.validate_on_submit(): 
        return redirect( url_for('addTasks.addQuestions'))

    return render_template('addTasks/addingFillInTheBlanksTypeQuestion.html',form=form)


@addTasks.route('/addingMUltipleChoiceQuestion', methods=['POST', 'GET'])
def addingMUltipleChoiceQuestion():
    if request.method == 'POST':
        tasks = request.form
        content = tasks["content"]
        options = tasks["options"].split("||")
        relatedtags = tasks["relatedtags"].split("||")
        answer = tasks["answer"].split("||")
        links = tasks["links"].split("||")

        task_content = jsonify(
            content=content,
            options=options,
            relatedtags=relatedtags,
            answer=answer,
            referencelinks=links,
        )
        print(task_content.data)

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
        links = tasks["referencelinks"].split("||")
        # inputfile = request.files["input"]
        # outputfile = request.files["output"]

        task_content = jsonify(
            title=title,
            description=description,
            instructions=instructions,
            constraints=constraints,
            examples=examples,
            solutionlanguage=solutionlanguage,
            answer=answer,
            links=links,
        )
        print(task_content.data)
        return render_template('addTasks/index.html', tasks=tasks)
    else:
        return render_template('addTasks/addingCodingTypeQuestion.html')
