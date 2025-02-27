from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.badge import Badge
from app.forms.badge_forms import BadgeForm

admin_badges_bp = Blueprint("admin_badges", __name__, url_prefix="/admin/badges")

def admin_required(func):
    """Decorador para restringir acceso solo a administradores."""
    from functools import wraps
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Acceso denegado. Solo administradores pueden entrar.", "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wraps(func)(wrapper)

@admin_badges_bp.route("/")
@admin_required
def badge_list():
    """Mostrar la lista de badges."""
    badges = Badge.query.order_by(Badge.min_score).all()
    return render_template("admin/badges.html", badges=badges)

@admin_badges_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add_badge():
    """Agregar un nuevo badge."""
    form = BadgeForm()
    if form.validate_on_submit():
        badge = Badge(
            name=form.name.data,
            description=form.description.data,
            min_score=form.min_score.data,
            image_url=form.image_url.data
        )
        db.session.add(badge)
        db.session.commit()
        flash("Badge creado con éxito.", "success")
        return redirect(url_for("admin_badges.badge_list"))
    return render_template("admin/add_badge.html", form=form)

@admin_badges_bp.route("/edit/<int:badge_id>", methods=["GET", "POST"])
@admin_required
def edit_badge(badge_id):
    """Editar un badge existente."""
    badge = Badge.query.get_or_404(badge_id)
    form = BadgeForm(obj=badge)
    if form.validate_on_submit():
        badge.name = form.name.data
        badge.description = form.description.data
        badge.min_score = form.min_score.data
        badge.image_url = form.image_url.data
        db.session.commit()
        flash("Badge actualizado con éxito.", "success")
        return redirect(url_for("admin_badges.badge_list"))
    return render_template("admin/edit_badge.html", form=form, badge=badge)

@admin_badges_bp.route("/delete/<int:badge_id>", methods=["POST"])
@admin_required
def delete_badge(badge_id):
    """Eliminar un badge."""
    badge = Badge.query.get_or_404(badge_id)
    db.session.delete(badge)
    db.session.commit()
    flash("Badge eliminado con éxito.", "danger")
    return redirect(url_for("admin_badges.badge_list"))
