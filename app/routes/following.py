from flask import Blueprint, redirect, render_template, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.activity import ActivityLog
from app.models.following_notifications import FollowingNotification
from app.models.list import List
from flask_wtf import FlaskForm
from wtforms import HiddenField

class EmptyForm(FlaskForm):
    pass

following_bp = Blueprint("following", __name__, url_prefix="/following")

@following_bp.route("/toggle/<int:list_id>", methods=["POST"]) 
@login_required
def toggle_follow(list_id):
    """Seguir o dejar de seguir una lista."""
    list_obj = List.query.get_or_404(list_id)

    if list_obj.user_id == current_user.id:
        flash("No puedes seguir tu propia lista.", "warning")
        return redirect(url_for("lists.view_list", list_id=list_id))

    if current_user.is_following(list_obj):
        current_user.unfollow_list(list_obj)
        action_text = "❌ dejó de seguir"
        flash("Has dejado de seguir la lista.", "info")
    else:
        current_user.follow_list(list_obj)
        action_text = "❤️ comenzó a seguir"
        flash("Ahora sigues esta lista.", "success")

    log = ActivityLog(user_id=current_user.id, list_id=list_id, action="follow",
                          message=f"{action_text} la lista '{list_obj.name}'.")
    db.session.add(log)
    db.session.commit()

    return redirect(url_for("lists.view_list", list_id=list_id))



@following_bp.route("/")
@login_required
def view_following():
    """Muestra todas las listas seguidas por el usuario, separando las actualizadas."""
    lists = current_user.following_lists
    updated_lists = [l for l in lists if l.has_unread_notifications()]
    normal_lists = [l for l in lists if not l.has_unread_notifications()]

    form = EmptyForm()  # ✅ Creamos un formulario vacío para el CSRF

    return render_template(
        "following/view_following.html",
        updated_lists=updated_lists if updated_lists else None,
        normal_lists=normal_lists if normal_lists else None,
        form=form  # ✅ Pasamos el formulario a la plantilla
    )


@following_bp.route("/mark_all_as_read", methods=["POST"])
@login_required
def mark_all_following_as_read():
    """Marca todas las notificaciones de listas seguidas como leídas."""
    for list_obj in current_user.following_lists:
        list_obj.mark_notifications_as_read(current_user)  # ✅ Pasamos el usuario

    db.session.commit()
    flash("Todas las notificaciones de listas seguidas han sido marcadas como leídas.", "success")
    return redirect(url_for("following.view_following"))


@following_bp.route("/notifications/read/<int:list_id>", methods=["POST"])
@login_required
def mark_list_as_read(list_id):
    """Marcar como leídas las notificaciones de una lista específica."""
    list_obj = List.query.get_or_404(list_id)

    # ✅ Llamar al nuevo método del modelo List
    list_obj.mark_notifications_as_read(current_user)

    flash(f"Las notificaciones de '{list_obj.name}' han sido marcadas como leídas.", "success")
    return redirect(url_for("following.view_following"))


@following_bp.route("/notifications")
@login_required
def view_following_notifications():
    """Muestra las notificaciones de las listas que sigue el usuario."""
    notifications = FollowingNotification.query.filter_by(user_id=current_user.id).order_by(FollowingNotification.timestamp.desc()).limit(5).all()
    
    return render_template("following/notifications.html", notifications=notifications)

