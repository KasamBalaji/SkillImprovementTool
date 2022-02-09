from flask_wtf import FlaskForm
from wtforms import  widgets, SelectMultipleField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField 
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.auth.models import User

SKILL_CHOICES=['C++','JAVA','PYTHON','OOPS','HTML','CSS','JAVASCRIPT','APPTITUDE','CODING']

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class FillInTheBlanksTypeQuestionForm(FlaskForm): 
    skill = MultiCheckboxField('Skills (Check all that apply)', choices=SKILL_CHOICES)
    content=TextAreaField("content",[])
    relatedTags=StringField("related tags",[DataRequired(),])
    answer=StringField("answer",[DataRequired(),])
    referenceLinks=TextAreaField('reference links',[DataRequired(),])
    submit=SubmitField('Submit') 
