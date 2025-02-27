from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.forms.user_forms import EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, ChangePasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from app import db
from app.models.user import User
from app.models.list import List, likes_table
from app.models.item import Item
from app.models.comment import Comment


users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/profile")
@login_required
def profile():
    """Perfil del usuario con estadísticas personales"""
    
    total_listas = List.query.filter_by(user_id=current_user.id).count()
    total_items = Item.query.join(List).filter(List.user_id == current_user.id).count()
    total_likes = db.session.query(func.count()).filter(
        likes_table.c.list_id == List.id, 
        likes_table.c.is_like == True, 
        List.user_id == current_user.id
    ).scalar() or 0
    total_dislikes = db.session.query(func.count()).filter(
        likes_table.c.list_id == List.id, 
        likes_table.c.is_like == False, 
        List.user_id == current_user.id
    ).scalar() or 0
    total_comentarios = Comment.query.join(List).filter(List.user_id == current_user.id).count()

    listas_usuario = List.query.filter_by(user_id=current_user.id).order_by(List.timestamp.desc()).limit(5).all()
    items_usuario = Item.query.join(List).filter(List.user_id == current_user.id).order_by(Item.id.desc()).limit(5).all()

    return render_template("user/profile.html",
                           total_listas=total_listas,
                           total_items=total_items,
                           total_likes=total_likes,
                           total_dislikes=total_dislikes,
                           total_comentarios=total_comentarios,
                           listas_usuario=listas_usuario,
                           items_usuario=items_usuario)


@users_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Perfil actualizado", "success")
        return redirect(url_for("users.profile"))
    return render_template("user/edit_profile.html", form=form)

@users_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("Instrucciones enviadas a tu correo", "info")
            # Aquí se enviaría un correo con un enlace para restablecer la contraseña
        else:
            flash("No existe un usuario con ese correo", "danger")
    return render_template("user/reset_password.html", form=form)

@users_bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.old_password.data):
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Contraseña actualizada", "success")
            return redirect(url_for("users.profile"))
        else:
            flash("Contraseña actual incorrecta", "danger")
    return render_template("user/change_password.html", form=form)
