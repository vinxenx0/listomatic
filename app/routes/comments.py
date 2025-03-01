from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.activity import ActivityLog
from app.models.comment import Comment
from app.forms.comment_forms import CommentForm

comments_bp = Blueprint("comments", __name__, url_prefix="/comments")


@comments_bp.route("/add/<int:list_id>", methods=["POST"])
@login_required
def add_comment(list_id):
    """Permitir que usuarios registrados añadan comentarios en listas públicas."""
    from app.models.list import List
    form = CommentForm()

    list_obj = List.query.get_or_404(list_id)
    if not list_obj.is_public:
        flash("No puedes comentar en listas privadas.", "danger")
        return redirect(url_for("lists.view_list", list_id=list_id))

    if form.validate_on_submit():
        new_comment = Comment(content=form.content.data,
                              user_id=current_user.id,
                              list_id=list_id)
        db.session.add(new_comment)
        db.session.commit()
        current_user.add_score(0.5)

        log = ActivityLog(user_id=current_user.id, list_id=list_id, action="comment",
                          message=f"💬 {current_user.username} comentó en '{list_obj.name}': \"{form.content.data[:50]}...\"")

        db.session.add(log)
        db.session.commit()
        if list_obj.owner.id != current_user.id:
            list_obj.owner.add_notification("comment", f"{current_user.username} comentó en tu lista '{list_obj.name}'.")

  
        flash("Comentario agregado con éxito!", "success")

    return redirect(url_for("lists.view_list", list_id=list_id))


@comments_bp.route("/delete/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    """Eliminar un comentario (solo el autor, dueño de la lista o admin pueden hacerlo)."""
    comment = Comment.query.get_or_404(comment_id)
    if current_user.id != comment.user_id and current_user.id != comment.list.user_id and not current_user.is_admin(
    ):
        flash("No tienes permiso para eliminar este comentario.", "danger")
        return redirect(url_for("lists.view_list", list_id=comment.list_id))

    db.session.delete(comment)
    db.session.commit()
    flash("Comentario eliminado con éxito.", "success")
    return redirect(url_for("lists.view_list", list_id=comment.list_id))
