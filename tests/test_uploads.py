import io
import pytest
from app import db
from app.models.list import List

@pytest.fixture
def create_test_list(app, test_user):
    """Crea una lista de prueba en la base de datos y devuelve su ID."""
    with app.app_context():
        test_list = List(name="Lista de prueba", user_id=test_user.id)
        db.session.add(test_list)
        db.session.commit()
        return test_list.id

def test_upload_valid_image(authenticated_client, app, create_test_list):
    """Test: Subir una imagen válida a una lista."""
    with app.app_context():  # ✅ Garantizar contexto de aplicación
        data = {
            "name": "Lista con imagen",
            "category": "Trabajo",
            "is_public": "true",
            "image": (io.BytesIO(b"test"), "test.png")  # 🔹 Simula archivo válido
        }

        response = authenticated_client.post("/lists/create", data=data, content_type="multipart/form-data", follow_redirects=True)

        assert response.status_code == 200
        assert b"Lista creada exitosamente" in response.data
        lista = List.query.filter_by(name="Lista con imagen").first()
        assert lista is not None
        assert lista.image_url.startswith("uploads/")

def test_reject_invalid_file_type(authenticated_client, app, create_test_list):
    """Test: Rechazar archivos con extensión no permitida."""
    with app.app_context():  # ✅ Garantizar contexto de aplicación
        data = {
            "name": "Lista con archivo inválido",
            "category": "Trabajo",
            "is_public": "true",
            "image": (io.BytesIO(b"test"), "test.txt")  # 🔹 Archivo no permitido
        }

        response = authenticated_client.post("/lists/create", data=data, content_type="multipart/form-data", follow_redirects=True)

        assert response.status_code == 200
        assert "Formato de imagen no permitido" in response.data.decode("utf-8")
