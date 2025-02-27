def test_dashboard_access_requires_login(client):
    """Test: la ruta /lists/dashboard requiere autenticación."""
    response = client.get("/lists/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert "Iniciar sesión" in response.data.decode("utf-8")

def test_dashboard_access_authenticated(client, init_database):
    """Test: usuario autenticado puede acceder a /lists/dashboard."""
    
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "testpassword"
    }, follow_redirects=True)

    assert response.status_code == 200  # ✅ Ahora el login debe ser exitoso
    assert "Mis Listas" in response.data.decode("utf-8")
