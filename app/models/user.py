from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)  # "user" o "admin"

    lists = db.relationship("List", backref="owner", lazy=True)

    def is_admin(self):
        """Verifica si el usuario es administrador."""
        return self.role == "admin"
