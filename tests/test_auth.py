from flask_login import current_user
from app.models.user import User
from werkzeug.security import check_password_hash

def test_register(client):
    """Test de registro de usuario."""
    response = client.post("/auth/register", data={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword",
        "confirm": "newpassword"
    }, follow_redirects=True)

    print(response.data.decode("utf-8"))  # 🔹 Para ver el mensaje real en la página

    assert response.status_code == 200
    assert "Tu cuenta ha sido creada! Ya puedes iniciar sesión." in response.data.decode("utf-8")  # ✅ Ajustar mensaje
    with client.application.app_context():
        user = User.query.filter_by(email="newuser@example.com").first()
        assert user is not None
        assert check_password_hash(user.password, "newpassword")

def test_login_success(client, test_user):
    """Test de inicio de sesión con credenciales correctas."""
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "testpassword"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Inicio de sesión exitoso" in response.data.decode("utf-8")

def test_login_failure(client, test_user):
    """Test de inicio de sesión con credenciales incorrectas."""
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "wrongpassword"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Credenciales incorrectas" in response.data.decode("utf-8")  # ✅ Convertir a string antes de comparar

def test_logout(authenticated_client):
    """Test de cierre de sesión."""
    response = authenticated_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert "Iniciar sesión" in response.data.decode("utf-8")
