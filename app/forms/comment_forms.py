from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    content = TextAreaField("Añadir Comentario", validators=[DataRequired(), Length(min=2, max=500)])
    submit = SubmitField("Publicar Comentario")


