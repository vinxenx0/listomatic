from flask import Blueprint, render_template
from app import db
from app.models.category import Category
from app.models.comment import Comment
from app.models.list import List, likes_table
from app.models.tag import Tag
from sqlalchemy.sql import func
from flask_wtf import FlaskForm

from app.models.user import User  # ✅ Importamos FlaskForm para CSRF

home_bp = Blueprint("home", __name__)

# ✅ Crear una clase de formulario vacía (necesaria para CSRF en botones)
class EmptyForm(FlaskForm):
    pass

@home_bp.route("/")
def home():
    """Página de inicio con listas públicas y estadísticas de categorías/etiquetas."""

    # ✅ Obtener listas públicas y ordenarlas por likes
    public_lists = List.query.filter_by(is_public=True).all()
    public_lists = sorted(public_lists, key=lambda l: l.count_likes(), reverse=True)

    total_lists = db.session.query(func.count(List.id)).scalar()
    total_users = db.session.query(func.count(User.id)).scalar()
    # ✅ Calcular el total de interacciones (likes, dislikes y comentarios)
    total_interactions = (
        db.session.query(func.count()).select_from(likes_table).scalar() or 0
    ) + db.session.query(func.count()).select_from(Comment).scalar()

    # ✅ Obtener las listas más populares en función de likes - dislikes
    trending_lists = (
        List.query
        .filter(List.is_public == True)
        .all()
    )
    trending_lists = sorted(trending_lists, key=lambda l: l.count_likes() - l.count_dislikes(), reverse=True)[:5]

    # ✅ Obtener las 5 listas más recientes
    latest_lists = List.query.filter_by(is_public=True).order_by(List.timestamp.desc()).limit(5).all()

    # ✅ Obtener el resto de listas que no están en `Tendencias` ni en `Últimas Listas`
    excluded_ids = {l.id for l in trending_lists + latest_lists}
    other_lists = List.query.filter(List.is_public == True, ~List.id.in_(excluded_ids)).order_by(List.timestamp.desc()).all()



    public_lists = List.query.filter_by(is_public=True).order_by(List.timestamp.desc()).limit(10).all()



    # ✅ Contar listas por categoría
    category_counts = {category.name: 0 for category in Category.get_all()}  # 🔥 Inicializa el dict correctamente
    for category_name, count in (
        db.session.query(List.category, func.count(List.id))
        .filter(List.is_public == True)
        .group_by(List.category)
        .all()
    ):
        category_counts[category_name] = count

    # ✅ Contar etiquetas en listas públicas
    tag_counts = dict(
        db.session.query(Tag.name, func.count(List.id))
        .join(List.tags)
        .filter(List.is_public == True)
        .group_by(Tag.name)
        .all()
    )  # Convertir a diccionario

    # ✅ Crear una instancia del formulario vacío
    form = EmptyForm()

    return render_template("index.html",
                           total_lists=total_lists,
                           total_users=total_users,
                           total_interactions=total_interactions,
                           trending_lists=trending_lists,
                           public_lists=latest_lists,
                           other_lists=other_lists,
                           category_counts=category_counts,
                           tag_counts=tag_counts,
                           form=form)
