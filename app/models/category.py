from sqlalchemy import select, func
from app import db
from sqlalchemy.orm import column_property

class Category(db.Model):
    """Modelo para almacenar las categorías dinámicas de las listas."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def count_lists(self):
        """Cuenta cuántas listas pertenecen a esta categoría."""
        from app.models.list import List  # ✅ Importamos aquí para evitar ciclo
        return db.session.query(List).filter_by(category_id=self.id).count()

    @staticmethod
    def get_all():
        """Devuelve todas las categorías ordenadas alfabéticamente."""
        return Category.query.order_by(Category.name).all()

    @staticmethod
    def get_choices():
        """Devuelve las categorías como una lista de opciones para los formularios."""
        return [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]
