from datetime import datetime
from app import db
from app.models.user import User

item_ratings = db.Table(
    "item_ratings",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("item_id", db.Integer, db.ForeignKey("item.id"), primary_key=True),
    db.Column("rating", db.Integer, nullable=False)  # 0 a 5 estrellas
)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), default="uploads/default_thumbnail.png")  # ✅ Solo la ruta relativa
    year = db.Column(db.Integer, nullable=True)  # Año opcional
    list_id = db.Column(db.Integer, db.ForeignKey("list.id"), nullable=False)
    list_count = db.Column(db.Integer, default=0)  # Número de listas en las que aparece

    ratings = db.relationship("User", secondary=item_ratings, backref="rated_items")

    def update_list_count(self):
        """Actualizar el número de listas en las que aparece este ítem."""
        self.list_count = db.session.query(Item).filter_by(content=self.content).count()
        db.session.commit()

    def average_rating(self):
        """Obtener el rating promedio del ítem."""
        from sqlalchemy.sql import func
        avg_rating = db.session.query(func.avg(item_ratings.c.rating)).filter_by(item_id=self.id).scalar()
        return round(avg_rating, 1) if avg_rating else 0
