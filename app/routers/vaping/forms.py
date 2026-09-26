# EUFit/app/routers/vaping/forms.py
from flask_wtf import FlaskForm
from wtforms import IntegerField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class LogForm(FlaskForm):
    puff_count = IntegerField(
        "Puff count",
        validators=[DataRequired(), NumberRange(min=0, max=5000)],
    )
    submit = SubmitField("Save")


class EditForm(FlaskForm):
    puff_count = IntegerField(
        "Puff count",
        validators=[DataRequired(), NumberRange(min=0, max=5000)],
    )
    recorded_at = DateTimeLocalField(
        "Date & time",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()],
    )
    submit = SubmitField("Update Record")
