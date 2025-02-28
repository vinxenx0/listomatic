import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash
from config import Config, DevelopmentConfig
from sqlalchemy.sql import func
from flask_wtf.csrf import CSRFProtect
import os
from config import config_dict

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

    """Crea y configura la aplicación Flask según el entorno."""
    
    # Detectar el entorno desde la variable de entorno FLASK_ENV
    env = os.getenv("FLASK_ENV", "development")
    app_config = config_dict.get(env, DevelopmentConfig)


    app = Flask(__name__, static_folder="static")
    app.config.from_object(app_config)
    #app.config.from_object(Config)
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
    from app.models.list import likes_table
    from app.models.comment import Comment

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
    from app.routes.admin_badges import admin_badges_bp

    app.register_blueprint(comments_bp, url_prefix="/comments")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(lists_bp, url_prefix="/lists")
    app.register_blueprint(items_bp, url_prefix="/items")
    app.register_blueprint(tags_bp, url_prefix="/tags")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(admin_badges_bp, url_prefix="/admin/badges")

    @app.cli.command("init-db")
    def init_db():
        """Inicializa la base de datos con datos de ejemplo si no existen."""
        with app.app_context():
            """Carga datos de prueba en la base de datos."""
            db.create_all()

            # ✅ Configuración global
            if not AppConfig.query.first():
                config = AppConfig()
                db.session.add(config)

            # ✅ Crear categorías
            default_categories = ["Trabajo", "Personal", "Compras", "Estudio", "Ocio"]
            for name in default_categories:
                if not Category.query.filter_by(name=name).first():
                    db.session.add(Category(name=name))
                    
            db.session.commit()
            db.session.flush()

            print("✅ Categorías creadas correctamente")

            # ✅ Crear usuarios de prueba
            if not User.query.first():
                admin = User(username="admin",
                            email="admin@example.com",
                            role="admin",
                            password=generate_password_hash("admin123", method="pbkdf2:sha256"))
                
                user1 = User(username="user1",
                            email="user1@example.com",
                            role="user",
                            password=generate_password_hash("user123", method="pbkdf2:sha256"))

                user2 = User(username="user2",
                            email="user2@example.com",
                            role="user",
                            password=generate_password_hash("user123", method="pbkdf2:sha256"))

                db.session.add_all([admin, user1, user2])
                db.session.commit()

                print("✅ Usuarios creados correctamente")

            # ✅ Crear listas de prueba
            admin = User.query.filter_by(username="admin").first()
            user1 = User.query.filter_by(username="user1").first()
            user2 = User.query.filter_by(username="user2").first()

            cat_trabajo = Category.query.filter_by(name="Trabajo").first()
            cat_ocio = Category.query.filter_by(name="Ocio").first()

            listas = [
                List(name="Tareas pendientes", user_id=admin.id, is_public=True, category=cat_trabajo),
                List(name="Películas por ver", user_id=user1.id, is_public=True, category=cat_ocio),
                List(name="Lista de compras", user_id=user2.id, is_public=True, category=Category.query.filter_by(name="Compras").first()),
            ]

            db.session.add_all(listas)
            db.session.commit()

            print("✅ Listas creadas correctamente")

            # ✅ Crear ítems en las listas
            items = [
                Item(content="Hacer informe mensual", list_id=listas[0].id, image_url="uploads/default_thumbnail.png"),
                Item(content="Revisar correos", list_id=listas[0].id, image_url="uploads/default_thumbnail.png"),
                Item(content="Ver 'Inception'", list_id=listas[1].id, image_url="uploads/default_thumbnail.png"),
                Item(content="Comprar leche", list_id=listas[2].id, image_url="uploads/default_thumbnail.png"),
                Item(content="Comprar pan", list_id=listas[2].id, image_url="uploads/default_thumbnail.png"),
            ]

            db.session.add_all(items)
            db.session.commit()

            print("✅ Ítems creados correctamente")

            # ✅ Crear comentarios en listas
            comments = [
                Comment(content="¡Buena lista!", user_id=user1.id, list_id=listas[0].id),
                Comment(content="Agrega más tareas", user_id=user2.id, list_id=listas[0].id),
                Comment(content="¡Esa película es genial!", user_id=admin.id, list_id=listas[1].id),
            ]

            db.session.add_all(comments)
            db.session.commit()

            print("✅ Comentarios creados correctamente")

            # ✅ Añadir likes y dislikes
            likes = [
                {"user_id": user1.id, "list_id": listas[0].id, "is_like": True},
                {"user_id": user2.id, "list_id": listas[0].id, "is_like": False},
                {"user_id": admin.id, "list_id": listas[1].id, "is_like": True},
            ]

            db.session.execute(likes_table.insert(), likes)
            db.session.commit()

            print("✅ Likes y dislikes añadidos")
            
            db.session.commit()
            print("✅ Base de datos inicializada correctamente")

    return app
