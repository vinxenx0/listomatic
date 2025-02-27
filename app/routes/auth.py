from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegisterForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.list import List

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        print("🔹 Usuario ya autenticado, redirigiendo...")
        return redirect(url_for("lists.dashboard"))

    form = LoginForm()
    #if request.method == "POST":

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)

            flash("Inicio de sesión exitoso", "success")

            return redirect(url_for("lists.dashboard"))

        flash("Credenciales incorrectas", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data,
                                                 method="pbkdf2:sha256")
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
