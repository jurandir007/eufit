# EUFit/app/routers/vaping/forms.py
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class LogForm(FlaskForm):
    puff_count = IntegerField(
        "Puff count",
        validators=[DataRequired(), NumberRange(min=0, max=5000)],
    )
    submit = SubmitField("Save")
