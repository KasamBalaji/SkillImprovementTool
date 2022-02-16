from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import DataRequired
class MCQForm(FlaskForm):
    def set(self,choices):
        print(choices)
        self.options.choices = choices
    options = RadioField('answer',validators=[DataRequired()])