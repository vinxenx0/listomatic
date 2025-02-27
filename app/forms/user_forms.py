from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class EditProfileForm(FlaskForm):
    username = StringField("Nombre de usuario", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Correo electrónico", validators=[DataRequired(), Email()])
    submit = SubmitField("Guardar cambios")

class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[DataRequired(), Email()])
    submit = SubmitField("Enviar instrucciones")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Nueva contraseña", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirmar contraseña", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Restablecer contraseña")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Contraseña actual", validators=[DataRequired()])
    new_password = PasswordField("Nueva contraseña", validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField("Confirmar nueva contraseña", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Actualizar contraseña")
