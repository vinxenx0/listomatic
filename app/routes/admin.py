from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy import func
from app import db
from app.forms.category_form import CategoryForm
from app.models.category import Category
from app.models.comment import Comment
from app.models.config import AppConfig
from app.forms.admin_forms import ConfigForm
from flask import Blueprint, render_template, url_for
from flask_login import current_user
from app import db
from app.models.config import AppConfig
from app.models.user import User
from app.models.list import List
from app.models.item import Item
from app.models.list import likes_table

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(func):
    """Decorador para restringir acceso solo a administradores."""
    from functools import wraps

    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Acceso denegado. Solo administradores pueden entrar.",
                  "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wraps(func)(wrapper)


@admin_bp.route("/")
@admin_required
def admin_dashboard():
    """Panel de administración con estadísticas generales y últimos registros."""
    config = AppConfig.get_config()

    total_users = db.session.query(User).count()
    total_lists = db.session.query(List).count()
    total_items = db.session.query(Item).count()
    total_comments = db.session.query(
        Comment).count()  # ✅ NUEVO: Contador de comentarios

    total_likes = db.session.query(likes_table).filter(
        likes_table.c.is_like == True).count()
    total_dislikes = db.session.query(likes_table).filter(
        likes_table.c.is_like == False).count()

    recent_users = User.query.order_by(User.id.desc()).limit(10).all()
    recent_lists = List.query.order_by(List.id.desc()).limit(10).all()
    recent_items = Item.query.order_by(Item.id.desc()).limit(10).all()
    recent_comments = Comment.query.order_by(Comment.id.desc()).limit(10).all()

    category_counts = dict(
        db.session.query(Category.name, func.count(List.id)).join(
            List, List.category_id == Category.id)  # ✅ Corrección correcta
        .filter(List.is_public == True).group_by(Category.name).all())

    return render_template("admin/dashboard.html",
                           config=config,
                           total_users=total_users,
                           total_lists=total_lists,
                           total_items=total_items,
                           total_comments=total_comments,
                           total_likes=total_likes,
                           total_dislikes=total_dislikes,
                           recent_users=recent_users,
                           recent_lists=recent_lists,
                           recent_items=recent_items,
                           recent_comments=recent_comments,
                           category_counts=category_counts)


@admin_bp.route("/config", methods=["GET", "POST"])
@admin_required
def edit_config():
    """Editar configuración global de la app."""
    config = AppConfig.get_config()
    form = ConfigForm(obj=config)

    if form.validate_on_submit():
        config.smtp_server = form.smtp_server.data
        config.smtp_port = form.smtp_port.data
        config.email_user = form.email_user.data
        config.email_password = form.email_password.data or config.email_password  # Mantener si está vacío
        config.categories = [
            c.strip() for c in form.categories.data.split(",") if c.strip()
        ]
        config.color_scheme = form.color_scheme.data
        config.app_url = form.app_url.data

        db.session.commit()
        flash("Configuración actualizada con éxito.", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin/edit_config.html", form=form)


@admin_bp.route("/categories")
@admin_required
def manage_categories():
    """Muestra la lista de categorías disponibles."""
    categories = Category.get_all()
    return render_template("admin/manage_categories.html",
                           categories=categories)


@admin_bp.route("/categories/add", methods=["GET", "POST"])
@admin_required
def add_category():
    """Añadir una nueva categoría."""
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data.strip())
        db.session.add(category)
        db.session.commit()
        flash("Categoría añadida con éxito", "success")
        return redirect(url_for("admin.manage_categories"))
    return render_template("admin/add_category.html", form=form)


@admin_bp.route("/categories/edit/<int:category_id>", methods=["GET", "POST"])
@admin_required
def edit_category(category_id):
    """Editar una categoría existente."""
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data.strip()
        db.session.commit()
        flash("Categoría actualizada con éxito", "success")
        return redirect(url_for("admin.manage_categories"))
    return render_template("admin/edit_category.html",
                           form=form,
                           category=category)


@admin_bp.route("/categories/delete/<int:category_id>", methods=["POST"])
@admin_required
def delete_category(category_id):
    """Eliminar una categoría."""
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash("Categoría eliminada con éxito", "danger")
    return redirect(url_for("admin.manage_categories"))


@admin_bp.route("/users")
@admin_required
def manage_users():
    """Lista de usuarios registrados"""
    users = User.query.order_by(User.id.desc()).all()
    return render_template("admin/manage_users.html", users=users)


@admin_bp.route("/badges")
@admin_required
def manage_badges():
    """Lista de badges disponibles"""
    from app.models.badge import Badge
    badges = Badge.get_all()
    return render_template("admin/manage_badges.html", badges=badges)