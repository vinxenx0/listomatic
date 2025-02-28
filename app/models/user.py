from flask_login import UserMixin
from app import db
from app.models.badge import Badge
from app.models.notification import Notification

# Tabla intermedia para la relación Usuario - Badge
user_badges = db.Table(
    "user_badges",
    db.Column("user_id",
              db.Integer,
              db.ForeignKey("user.id"),
              primary_key=True),
    db.Column("badge_id",
              db.Integer,
              db.ForeignKey("badge.id"),
              primary_key=True))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    theme = db.Column(db.String(10), default="light")  
    role = db.Column(db.String(20), default="user",
                     nullable=False)  # "user" o "admin"

    # Nuevo campo de puntuación
    score = db.Column(db.Integer, default=0, nullable=False)

    lists = db.relationship("List", backref="owner", lazy=True)
    badges = db.relationship("Badge", secondary=user_badges, backref="users")

    notifications = db.relationship("Notification", backref="user", lazy=True)

    def unread_notifications_count(self):
        """Devuelve el número de notificaciones no leídas."""
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()

    def get_notifications(self):
        """Obtiene las notificaciones ordenadas por fecha."""
        return Notification.query.filter_by(user_id=self.id).order_by(Notification.timestamp.desc()).all()

    def add_notification(self, type, message):
        """Añade una nueva notificación al usuario."""
        notification = Notification(user_id=self.id, type=type, message=message)
        db.session.add(notification)
        db.session.commit()

    def is_admin(self):
        """Verifica si el usuario es administrador."""
        return self.role == "admin"

    def add_score(self, points):
        """Añadir puntos al usuario y actualizar sus badges."""
        self.score += points
        db.session.commit()
        self.update_badges()

    def update_badges(self):
        """Asignar badges según la puntuación."""
        from app.models.badge import Badge  # ✅ Importación aquí para evitar ciclos
        badges = Badge.query.order_by(Badge.min_score).all()

        for badge in badges:
            if self.score >= badge.min_score and badge not in self.badges:
                self.badges.append(badge)

        db.session.commit()

    def assign_badges(self):
        """Asigna badges al usuario según su puntuación."""
        available_badges = Badge.query.all()
        for badge in available_badges:
            if self.score >= badge.min_score and badge not in self.badges:
                self.badges.append(badge)
        db.session.commit()

    def toggle_theme(self):
        """Alterna entre 'light' y 'dark'."""
        self.theme = "dark" if self.theme == "light" else "light"
        db.session.commit()
