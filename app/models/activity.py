from datetime import datetime
from app import db

class ActivityLog(db.Model):
    """Modelo para registrar la actividad de los usuarios en listas."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey("list.id"), nullable=True)  # Puede ser nulo para eventos generales
    action = db.Column(db.String(50), nullable=False)  # "create_list", "comment", "like", "dislike", "follow"
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref="activities")
    list = db.relationship("List", backref="activities")
