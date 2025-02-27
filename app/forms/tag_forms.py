from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class TagForm(FlaskForm):
    name = StringField("Nombre de la Etiqueta", validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField("Crear Etiqueta")
