from flask_wtf import FlaskForm
from wtforms import SelectMultipleField,SubmitField, widgets
from wtforms.validators import DataRequired,ValidationError

def validate_skills(form,field):
    if len(field.data)<=0:
        raise ValidationError("Skills Chosen Can't be Empty")

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class SkillForm(FlaskForm):
    # Insert Skill Names from DBMS Query
    skills = MultiCheckboxField('Skills', choices=[('C++','C++'),('Java','Java'),('HTML','HTML'),('CSS','CSS'),('JS','JS')], validators=[validate_skills])
    submit1 = SubmitField(label='Test Yourself')
    submit2 = SubmitField(label='Learning Session')