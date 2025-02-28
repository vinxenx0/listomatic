# -*- coding: utf-8 -*-


import pytest
import os
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="session")
def test_db_path():
    """Define la ruta de la base de datos de pruebas en un archivo separado."""
    test_db = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "test.db"))
  

    return test_db


@pytest.fixture(scope="session")
def app(test_db_path):
    """Crea una aplicación Flask para pruebas con una base de datos separada."""
    os.environ["FLASK_ENV"] = "testing"  # 🔹 Asegura que estamos en modo TEST
    os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{test_db_path}"

    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI":
        f"sqlite:///{test_db_path}",   
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    print(
        f"Base de datos configurada: {app.config['SQLALCHEMY_DATABASE_URI']}"
    )

    return app


@pytest.fixture(scope="session")
def app_context(app):
    """Mantiene el contexto de la aplicación activo para todas las pruebas."""
    with app.app_context():
        db.create_all()
        yield  # Permite que las pruebas se ejecuten dentro del contexto
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app, app_context):
    """Cliente de pruebas con contexto activo."""
    return app.test_client()


@pytest.fixture
def test_user(app_context):
    """Crea un usuario de prueba y lo devuelve con una sesión activa."""
    user = db.session.query(User).filter_by(email="test@example.com").first()

    if not user:  
        user = User(username="testuser",
                    email="test@example.com",
                    password=generate_password_hash("testpassword"))
        db.session.add(user)
        db.session.commit()

    db.session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Cliente autenticado con un usuario de prueba."""
    client.post("/auth/login",
                data={
                    "email": test_user.email,
                    "password": "testpassword"
                },
                follow_redirects=True)
    return client


@pytest.fixture(scope="function", autouse=True)
def cleanup_db():
    """Limpia la base de datos después de cada test sin causar errores de sesión."""
    yield
    db.session.rollback()
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
