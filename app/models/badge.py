from app import db

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    min_score = db.Column(db.Integer, nullable=False)  # Puntuación mínima requerida
    image_url = db.Column(db.String(255), nullable=False)  # Ruta de la imagen

    def __repr__(self):
        return f"<Badge {self.name} ({self.min_score} puntos)>"
