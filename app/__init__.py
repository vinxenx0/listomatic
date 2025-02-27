import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash
from config import Config
from sqlalchemy.sql import func
from flask_wtf.csrf import CSRFProtect
import os

# Definir la carpeta de subida de imágenes
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Ruta base del proyecto
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

# Inicialización de extensiones
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"  #  Redirigir a login si no está autenticado
migrate = Migrate()
bootstrap = Bootstrap5()
csrf = CSRFProtect()


def create_app():

    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    csrf.init_app(app)

    from app.models.user import User
    from app.models.list import List
    from app.models.item import Item
    from app.models.category import Category
    from app.models.config import AppConfig

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.lists import lists_bp
    from app.routes.items import items_bp
    from app.routes.tags import tags_bp
    from app.routes.users import users_bp
    from app.routes.home import home_bp
    from app.routes.comments import comments_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(comments_bp, url_prefix="/comments")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(lists_bp, url_prefix="/lists")
    app.register_blueprint(items_bp, url_prefix="/items")
    app.register_blueprint(tags_bp, url_prefix="/tags")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.cli.command("init-db")
    def init_db():
        """Inicializa la base de datos con datos de ejemplo si no existen."""
        with app.app_context():
            db.create_all()

            # ✅ Crear configuración global si no existe
            if not AppConfig.query.first():
                config = AppConfig()
                db.session.add(config)

            # ✅ Crear categorías por defecto si no existen
            default_categories = ["Trabajo", "Personal", "Compras", "Estudio", "Ocio"]
            for name in default_categories:
                if not Category.query.filter_by(name=name).first():
                    db.session.add(Category(name=name))

            db.session.commit()
            print("✅ Categorías creadas correctamente")

            # ✅ Crear usuarios de ejemplo
            if not User.query.first():
                admin = User(username="admin",
                             email="admin@example.com",
                             role="admin",
                             password=generate_password_hash(
                                 "admin123", method="pbkdf2:sha256"))
                user = User(username="usuario",
                            email="usuario@example.com",
                            role="user",
                            password=generate_password_hash(
                                "user123", method="pbkdf2:sha256"))
                db.session.add_all([admin, user])
                db.session.commit()

                category_compras = Category.query.filter_by(name="Compras").first()
                category_ocio = Category.query.filter_by(name="Ocio").first()

                listas_admin = [
                    List(name="Lista de Compras",
                         user_id=admin.id,
                         is_public=True,
                         category_id=category_compras.id),
                    List(name="Películas por Ver",
                         user_id=admin.id,
                         is_public=True,
                         category_id=category_ocio.id)
                ]

                db.session.add_all(listas_admin)
                db.session.commit()

                # ✅ Añadir ítems a las listas
                items = [
                    Item(content="Leche",
                         list_id=listas_admin[0].id,
                         image_url="uploads/default_thumbnail.png"),
                    Item(content="Pan",
                         list_id=listas_admin[0].id,
                         image_url="uploads/default_thumbnail.png"),
                    Item(content="Interestelar",
                         list_id=listas_admin[1].id,
                         image_url="uploads/default_thumbnail.png"),
                    Item(content="El Padrino",
                         list_id=listas_admin[1].id,
                         image_url="uploads/default_thumbnail.png")
                ]
                db.session.add_all(items)
                db.session.commit()

            db.session.commit()
            print("✅ Base de datos inicializada correctamente")

    return app
