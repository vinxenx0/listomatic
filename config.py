import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

class Config:
    """Configuración base (heredada por Dev y Prod)"""
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
    SESSION_COOKIE_HTTPONLY = os.getenv("SESSION_COOKIE_HTTPONLY", "True") == "True"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

class DevelopmentConfig(Config):
    """Configuración para desarrollo (SQLite)"""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL_DEV", "sqlite:///lists.db")
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción (MySQL)"""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL_PROD")
    DEBUG = False

# Mapeo de entornos
config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
