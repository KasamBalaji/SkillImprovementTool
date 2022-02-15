from flask_wtf import FlaskForm
from wtforms import  widgets, SelectMultipleField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField 
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models import User

SKILL_CHOICES=['C++','JAVA','PYTHON','OOPS','HTML','CSS','JAVASCRIPT','APPTITUDE','CODING']

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
# refer https://gist.github.com/imwilsonxu/1e7343426135b4a34ce78574012a8f62
class FillInTheBlanksTypeQuestionForm(FlaskForm): 
    skill = MultiCheckboxField('Skills (Check all that apply)', choices=SKILL_CHOICES)
    # skill = SelectMultipleField("skill", choices=SKILL_CHOICES, option_widget=None,render_kw={"multiple": "multiple"})
    # language = SelectMultipleField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    content=TextAreaField("content",[])
    relatedTags=StringField("related tags",[DataRequired(),])
    answer=StringField("answer",[DataRequired(),])
    referenceLinks=TextAreaField('reference links',[DataRequired(),])
    submit=SubmitField('Submit') 
