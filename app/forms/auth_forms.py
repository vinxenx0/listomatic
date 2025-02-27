from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = EmailField("Correo Electrónico", validators=[DataRequired(), Email()])  # 🔥 CAMBIO A `EmailField`
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Iniciar Sesión")



class RegisterForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Correo Electrónico", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirmar Contraseña", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Registrarse")
