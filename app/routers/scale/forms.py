# EUFit/app/routers/scale/forms.py
from flask_wtf import FlaskForm
from wtforms import FloatField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class LogForm(FlaskForm):
    """Formulário de registo de pesagem.

    Obrigatórios : peso, gordura, viceral
    Opcionais    : musculo, basal, idade
    """
    peso    = FloatField("Peso (kg)",         validators=[DataRequired(), NumberRange(min=1,   max=500)],  render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    gordura = FloatField("Gordura (%)",       validators=[DataRequired(), NumberRange(min=0,   max=100)],  render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    viceral = FloatField("Visceral",          validators=[DataRequired(), NumberRange(min=0,   max=50)],   render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    musculo = FloatField("Músculo (%)",       validators=[Optional(),     NumberRange(min=0,   max=100)],  render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    basal   = FloatField("Basal (kcal)",      validators=[Optional(),     NumberRange(min=500, max=5000)], render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    idade   = FloatField("Idade metabólica",  validators=[Optional(),     NumberRange(min=1,   max=120)],  render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    submit  = SubmitField("Save")


class EditForm(FlaskForm):
    """Formulário de edição de registo existente."""
    carimbo = DateTimeLocalField("Date & time", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    peso    = FloatField("Peso (kg)",         validators=[DataRequired(), NumberRange(min=1,   max=500)],  render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    gordura = FloatField("Gordura (%)",       validators=[DataRequired(), NumberRange(min=0,   max=100)],  render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    viceral = FloatField("Visceral",          validators=[DataRequired(), NumberRange(min=0,   max=50)],   render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    musculo = FloatField("Músculo (%)",       validators=[Optional(),     NumberRange(min=0,   max=100)],  render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    basal   = FloatField("Basal (kcal)",      validators=[Optional(),     NumberRange(min=500, max=5000)], render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    idade   = FloatField("Idade metabólica",  validators=[Optional(),     NumberRange(min=1,   max=120)],  render_kw={"inputmode": "numeric", "pattern": "[0-9]*"})
    submit  = SubmitField("Update Record")
