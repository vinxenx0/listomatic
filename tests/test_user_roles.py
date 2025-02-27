from flask_login import current_user
from app.models.user import User
from app import db

def test_user_role_is_default_user(app, init_database):
    """Test: el rol de usuario es 'user' por defecto."""
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None  # ✅ Ahora el usuario debe existir
        assert user.role == "user"



def test_admin_role(app, init_database):
    """Test: asignación y verificación de rol 'admin'."""
    with app.app_context():
        admin = User(username="admin", email="admin@example.com", password="adminpass", role="admin")
        db.session.add(admin)
        db.session.commit()

        assert admin.role == "admin"
        assert admin.is_admin() is True
