from app import db
from sqlalchemy.dialects.postgresql import JSON

class AppConfig(db.Model):
    """Configuración global de la aplicación, accesible solo por administradores."""
    id = db.Column(db.Integer, primary_key=True)
    
    # Configuración de correo
    smtp_server = db.Column(db.String(255), nullable=False, default="smtp.example.com")
    smtp_port = db.Column(db.Integer, nullable=False, default=587)
    email_user = db.Column(db.String(255), nullable=False, default="admin@example.com")
    email_password = db.Column(db.String(255), nullable=False, default="")  # 🔹 Encriptar en producción
    
    # Categorías de listas (JSON)
    categories = db.Column(JSON, nullable=False, default=lambda: ["Trabajo", "Personal", "Compras", "Otros"])
    
    # Usuarios con acceso a la API
    api_users = db.Column(JSON, nullable=False, default=lambda: {})  # {"username": "hashed_password"}
    
    # Badges y sistema de puntuación
    badges = db.Column(JSON, nullable=False, default=lambda: {
        "Novato": {"score": 100, "image": "badges/novato.png"},
        "Experto": {"score": 500, "image": "badges/experto.png"},
        "Maestro": {"score": 1000, "image": "badges/maestro.png"}
    })
    
    # Configuración de colores (tema visual)
    color_scheme = db.Column(db.String(50), default="light")  # "light" o "dark"
    
    # URL principal
    app_url = db.Column(db.String(255), default="https://miapp.com")

    @staticmethod
    def get_config():
        """Obtiene la configuración global, si no existe la crea."""
        config = AppConfig.query.first()
        if not config:
            config = AppConfig()
            db.session.add(config)
            db.session.commit()
        return config
