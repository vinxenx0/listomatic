from datetime import datetime
from app import db

class FollowingNotification(db.Model):
    """Modelo para notificaciones de listas seguidas."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey("list.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # "update", "new_item"
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def mark_as_read(self):
        """Marcar la notificación como leída."""
        self.is_read = True
        db.session.commit()

