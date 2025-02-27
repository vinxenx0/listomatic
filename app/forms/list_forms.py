from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from app.models.category import Category

class ListForm(FlaskForm):
    name = StringField("Nombre de la Lista", validators=[DataRequired(), Length(min=3, max=50)])
    category = SelectField("Categoría", choices=[], coerce=int)  # 🔥 Debe ser un `int` (ID de la categoría)
    is_public = BooleanField("Lista Pública")
    tags = StringField("Etiquetas (separadas por comas)", validators=[Optional(), Length(max=100)])
    icon = StringField("Icono (opcional)", validators=[Optional(), Length(max=50)])
    image = FileField("Imagen de Portada (Opcional)")
    submit = SubmitField("Guardar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]



class ItemForm(FlaskForm):
    content = TextAreaField("Elemento", validators=[DataRequired(), Length(min=1, max=255)])
    image = FileField("Subir Imagen (Opcional)")
    submit = SubmitField("Añadir Ítem")
