from app import db
from app.models.list import List
from app.models.comment import Comment

def test_add_comment(authenticated_client, test_user):
    """Test: Agregar un comentario a una lista pública."""
    # ✅ Corregido: Eliminado `with db.session.begin()`
    test_list = List(name="Lista pública", user_id=test_user.id, is_public=True)
    db.session.add(test_list)
    db.session.commit()  # ✅ Confirmamos la inserción antes de hacer la petición

    response = authenticated_client.post(f"/comments/add/{test_list.id}", data={
        "content": "Este es un comentario de prueba."
    }, follow_redirects=True)

    assert response.status_code == 200
    assert Comment.query.filter_by(content="Este es un comentario de prueba.").first() is not None
    assert "Comentario agregado con éxito!" in response.data.decode("utf-8")  

def test_cannot_comment_on_private_list(authenticated_client, test_user):
    """Test: No se puede comentar en listas privadas."""
    test_list = List(name="Lista privada", user_id=test_user.id, is_public=False)
    db.session.add(test_list)
    db.session.commit()  # ✅ Confirmamos la inserción

    response = authenticated_client.post(f"/comments/add/{test_list.id}", data={
        "content": "Comentario en lista privada."
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "No puedes comentar en listas privadas." in response.data.decode("utf-8")  

def test_delete_comment(authenticated_client, test_user):
    """Test: Eliminar un comentario (solo autor, dueño de la lista o admin pueden)."""
    # 🔹 PRIMERO se crea y confirma la lista
    test_list = List(name="Lista con comentario", user_id=test_user.id, is_public=True)
    db.session.add(test_list)
    db.session.commit()  # ✅ Confirmamos la inserción en la DB

    # 🔹 RECUPERAMOS el ID de la lista desde la DB antes de crear el comentario
    test_list = List.query.filter_by(name="Lista con comentario").first()

    # 🔹 AHORA se crea el comentario con el `list_id` correcto
    test_comment = Comment(content="Comentario a eliminar", user_id=test_user.id, list_id=test_list.id)
    db.session.add(test_comment)
    db.session.commit()  # ✅ Confirmamos la inserción

    response = authenticated_client.post(f"/comments/delete/{test_comment.id}", follow_redirects=True)

    assert response.status_code == 200
    assert Comment.query.get(test_comment.id) is None  # ✅ Debe estar eliminado
    assert "Comentario eliminado con éxito." in response.data.decode("utf-8")
