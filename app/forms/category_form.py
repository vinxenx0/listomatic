from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class CategoryForm(FlaskForm):
    name = StringField("Nombre de la Categoría", validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField("Guardar")
