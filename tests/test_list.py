import pytest
from app import db
from app.models.user import User
from app.models.list import List
from app.models.tag import Tag
from werkzeug.security import generate_password_hash

@pytest.fixture
def test_user(app):
    """Crea un usuario de prueba."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("testpassword")
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def authenticated_client(client, test_user):
    """Cliente autenticado con un usuario de prueba."""
    client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "testpassword"
    }, follow_redirects=True)
    return client

def test_create_list(authenticated_client, app):
    """Test: Creación de una nueva lista."""
    response = authenticated_client.post("/lists/create", data={
        "name": "Lista de pruebas",
        "category": "Trabajo",
        "is_public": "true",
        "tags": "tarea, importante"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Lista creada exitosamente" in response.data.decode("utf-8")

    with app.app_context():
        assert List.query.filter_by(name="Lista de pruebas").first() is not None
def test_edit_list(authenticated_client, test_user, app):
    """Test: Edición de una lista."""
    with app.app_context():
        test_user = db.session.merge(test_user)  # ✅ SOLUCIÓN para evitar DetachedInstanceError
        test_list = List(name="Lista original", user_id=test_user.id)
        db.session.add(test_list)
        db.session.commit()
        db.session.refresh(test_list)

    response = authenticated_client.post(f"/lists/edit/{test_list.id}", data={
        "name": "Lista editada",
        "category": "Personal",
        "is_public": "false"
    }, follow_redirects=True)

    with app.app_context():
        updated_list = List.query.get(test_list.id)
        assert response.status_code == 200
        assert updated_list.name == "Lista editada"
        assert updated_list.category == "Personal"
        assert updated_list.is_public is False


def test_delete_list(authenticated_client, test_user, app):
    """Test: Eliminación de una lista."""
    with app.app_context():
        test_user = db.session.merge(test_user)  # ✅ SOLUCIÓN para evitar DetachedInstanceError
        test_list = List(name="Lista a eliminar", user_id=test_user.id)
        db.session.add(test_list)
        db.session.commit()
        db.session.refresh(test_list)

    response = authenticated_client.post(f"/lists/delete/{test_list.id}", follow_redirects=True)

    with app.app_context():
        assert response.status_code == 200
        assert List.query.get(test_list.id) is None
        assert "Lista eliminada" in response.data.decode("utf-8")


def test_list_filter_by_category(client, app, test_user):
    """Test: Filtrar listas por categoría."""
    with app.app_context():
        test_user = db.session.merge(test_user)  # ✅ SOLUCIÓN para evitar DetachedInstanceError
        list1 = List(name="Lista Trabajo", category="Trabajo", user_id=test_user.id)
        list2 = List(name="Lista Personal", category="Personal", user_id=test_user.id)
        db.session.add_all([list1, list2])
        db.session.commit()

    response = client.get("/lists/category/Trabajo")

    assert response.status_code == 200
    assert "Lista Trabajo" in response.data.decode("utf-8")
    assert "Lista Personal" not in response.data.decode("utf-8")  # ✅ Asegura que no se mezclen categorías
