from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.notification import Notification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

@notifications_bp.route("/")
@login_required
def view_all():
    """Muestra todas las notificaciones del usuario."""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return render_template("notifications/view_all.html", notifications=notifications)

@notifications_bp.route("/mark_as_read/<int:notification_id>")
@login_required
def mark_as_read(notification_id):
    """Marca una notificación como leída."""
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return redirect(url_for("notifications.view_all"))

    notification.is_read = True
    db.session.commit()
    return redirect(url_for("notifications.view_all"))

@notifications_bp.route("/clear")
@login_required
def clear_notifications():
    """Elimina todas las notificaciones del usuario."""
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for("notifications.view_all"))
