# EUFit/app/routers/scale/forms.py
from flask_wtf import FlaskForm
from wtforms import FloatField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class LogForm(FlaskForm):
    """Formulário de registo de pesagem.

    Obrigatórios : peso, gordura, viceral
    Opcionais    : musculo, basal, idade
    """
    peso    = FloatField("Peso (kg)",         validators=[DataRequired(), NumberRange(min=1,   max=500)])
    gordura = FloatField("Gordura (%)",       validators=[DataRequired(), NumberRange(min=0,   max=100)])
    viceral = FloatField("Visceral",          validators=[DataRequired(), NumberRange(min=0,   max=50)])
    musculo = FloatField("Músculo (%)",       validators=[Optional(),     NumberRange(min=0,   max=100)])
    basal   = FloatField("Basal (kcal)",      validators=[Optional(),     NumberRange(min=500, max=5000)])
    idade   = FloatField("Idade metabólica",  validators=[Optional(),     NumberRange(min=1,   max=120)])
    submit  = SubmitField("Save")


class EditForm(FlaskForm):
    """Formulário de edição de registo existente."""
    carimbo = DateTimeLocalField("Date & time", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    peso    = FloatField("Peso (kg)",         validators=[DataRequired(), NumberRange(min=1,   max=500)])
    gordura = FloatField("Gordura (%)",       validators=[DataRequired(), NumberRange(min=0,   max=100)])
    viceral = FloatField("Visceral",          validators=[DataRequired(), NumberRange(min=0,   max=50)])
    musculo = FloatField("Músculo (%)",       validators=[Optional(),     NumberRange(min=0,   max=100)])
    basal   = FloatField("Basal (kcal)",      validators=[Optional(),     NumberRange(min=500, max=5000)])
    idade   = FloatField("Idade metabólica",  validators=[Optional(),     NumberRange(min=1,   max=120)])
    submit  = SubmitField("Update Record")
