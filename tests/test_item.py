import pytest
from app import db
from app.models.list import List
from app.models.item import Item

def test_add_item(authenticated_client, test_user, app):
    """Test: Agregar un ítem a una lista."""
    with app.app_context():
        test_list = List(name="Lista con ítems", user_id=test_user.id)
        db.session.add(test_list)
        db.session.commit()
        list_id = test_list.id  # Guardamos el ID antes de salir del contexto

    response = authenticated_client.post(f"/items/add/{list_id}", data={
        "content": "Nuevo ítem"
    }, follow_redirects=True)

    with app.app_context():
        assert response.status_code == 200
        assert Item.query.filter_by(content="Nuevo ítem", list_id=list_id).first() is not None
        assert "Ítem agregado con éxito!" in response.data.decode("utf-8")

def test_delete_item(authenticated_client, test_user, app):
    """Test: Eliminar un ítem de una lista."""
    with app.app_context():
        test_list = List(name="Lista con ítem", user_id=test_user.id)
        db.session.add(test_list)
        db.session.commit()
        list_id = test_list.id  # Guardamos el ID antes de salir del contexto

        test_item = Item(content="Ítem a eliminar", list_id=list_id)
        db.session.add(test_item)
        db.session.commit()
        item_id = test_item.id  # Guardamos el ID antes de salir del contexto

    response = authenticated_client.post(f"/items/delete/{item_id}", follow_redirects=True)

    with app.app_context():
        assert response.status_code == 200
        assert Item.query.get(item_id) is None  # Confirma que el ítem ha sido eliminado
        assert "Ítem eliminado" in response.data.decode("utf-8")
