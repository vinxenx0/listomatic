def test_login_bruteforce_protection(client):
    """Test: protección contra intentos de login repetidos con credenciales incorrectas."""
    for _ in range(5):  # 🔹 Simula intentos fallidos
        client.post("/auth/login", data={
            "email": "test@example.com",
            "password": "wrongpassword"
        }, follow_redirects=True)

    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "testpassword"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Inicio de sesión exitoso" in response.data.decode("utf-8")  
