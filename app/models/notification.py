from datetime import datetime
from app import db

class Notification(db.Model):
    """Modelo para almacenar notificaciones de usuarios."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # Usuario que recibe la notificación
    type = db.Column(db.String(50), nullable=False)  # "like", "comment", "rating"
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def mark_as_read(self):
        """Marcar la notificación como leída."""
        self.is_read = True
        db.session.commit()
