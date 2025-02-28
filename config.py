import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base para todos los entornos."""
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
    SESSION_COOKIE_HTTPONLY = os.getenv("SESSION_COOKIE_HTTPONLY", "True") == "True"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", None)
    SSL_KEY_PATH = os.getenv("SSL_KEY_PATH", None)

class DevelopmentConfig(Config):
    """Configuración para desarrollo (con SQLite y SSL en Flask)."""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL_DEV", "sqlite:///lists.db")
    DEBUG = True
    USE_SSL = os.getenv("USE_SSL", "False") == "True"  # 🔹 Solo en Dev

class ProductionConfig(Config):
    """Configuración para producción (MySQL sin SSL en Flask, Nginx lo maneja)."""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL_PROD")
    DEBUG = False
    USE_SSL = False  # 🔹 Flask no usa SSL en producción, lo maneja Nginx

# Mapeo de entornos
config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
