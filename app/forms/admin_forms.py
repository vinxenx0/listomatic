from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Optional

class ConfigForm(FlaskForm):
    """Formulario para actualizar la configuración general."""
    smtp_server = StringField("Servidor SMTP", validators=[DataRequired()])
    smtp_port = IntegerField("Puerto SMTP", validators=[DataRequired()])
    email_user = StringField("Correo del sistema", validators=[DataRequired(), Email()])
    email_password = PasswordField("Contraseña SMTP (Opcional)", validators=[Optional()])
    categories = TextAreaField("Categorías (separadas por comas)", validators=[Optional()])
    color_scheme = SelectField("Esquema de colores", choices=[("light", "Claro"), ("dark", "Oscuro")])
    app_url = StringField("URL de la aplicación", validators=[DataRequired()])
    
    submit = SubmitField("Guardar cambios")
