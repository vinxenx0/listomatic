from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange

class BadgeForm(FlaskForm):
    name = StringField("Nombre del Badge", validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField("Descripción", validators=[Length(max=255)])
    min_score = IntegerField("Puntos necesarios", validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField("URL de la imagen", validators=[DataRequired(), Length(max=255)])
    submit = SubmitField("Guardar")
