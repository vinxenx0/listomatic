from flask import Blueprint, render_template
from app import db
from app.models.category import Category
from app.models.list import List
from app.models.tag import Tag
from sqlalchemy.sql import func

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    """Página de inicio con listas públicas y estadísticas de categorías/etiquetas."""

    # ✅ Primero obtenemos las listas públicas
    public_lists = List.query.filter_by(is_public=True).all()

    # ✅ Luego ordenamos en memoria usando el método count_likes()
    public_lists = sorted(public_lists,
                          key=lambda l: l.count_likes(),
                          reverse=True)

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
    tag_counts = (db.session.query(Tag.name, func.count(List.id)).join(
        List.tags).filter(List.is_public == True).group_by(Tag.name).all())

    tag_counts = dict(
        tag_counts
    )  # Convertir a diccionario para facilitar acceso en la plantilla

    return render_template("index.html",
                           public_lists=public_lists,
                           category_counts=category_counts,
                           tag_counts=tag_counts)
