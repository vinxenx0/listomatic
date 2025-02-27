import uuid
from datetime import datetime
from app import db
from app.models.comment import Comment
from app.models.tag import list_tags
from app.models.user import User

likes_table = db.Table(
    "likes",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("list_id", db.Integer, db.ForeignKey("list.id"), primary_key=True),
    db.Column("is_like", db.Boolean, nullable=False)  # ✅ Registra si es un like o dislike
)

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    icon = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(255), nullable=True, default="uploads/default_thumbnail.png")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    items = db.relationship("Item", backref="list", lazy=True)
    tags = db.relationship("Tag", secondary=list_tags, backref="lists", lazy="dynamic")
    liked_by = db.relationship("User", secondary=likes_table, backref="liked_lists")
    comments = db.relationship("Comment", back_populates="list_obj", lazy=True, cascade="all, delete-orphan")

    category_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete="SET NULL"), nullable=True)
    category = db.relationship("Category", backref="lists")  # ✅ Relación SQLAlchemy con Category

    def category_name(self):
        """Devuelve el nombre de la categoría o 'Sin categoría' si no tiene."""
        return self.category.name if self.category else "Sin categoría"

    def count_likes(self):
        """Cuenta cuántos likes tiene la lista."""
        return db.session.query(likes_table).filter_by(list_id=self.id, is_like=True).count() or 0

    def count_dislikes(self):
        """Cuenta cuántos dislikes tiene la lista."""
        return db.session.query(likes_table).filter_by(list_id=self.id, is_like=False).count() or 0

    def count_comments(self):
        """Cuenta el número de comentarios en la lista."""
        return db.session.query(Comment).filter_by(list_id=self.id).count()


    @staticmethod
    def category_count():
        """Devuelve un diccionario con el número de listas por categoría."""
        from sqlalchemy.sql import func
        results = db.session.query(List.category, func.count(
            List.id)).group_by(List.category).all()
        return {category: count for category, count in results}

    def toggle_privacy(self):
        """Alternar entre pública y privada."""
        self.is_public = not self.is_public

    def add_like(self, user):
        """Añadir un like de un usuario."""
        if user not in self.liked_by:
            self.liked_by.append(user)
            self.likes += 1

    def remove_like(self, user):
        """Quitar un like de un usuario."""
        if user in self.liked_by:
            self.liked_by.remove(user)
            self.likes -= 1 if self.likes > 0 else 0
