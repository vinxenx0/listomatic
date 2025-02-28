import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask import current_app
from app import db
from app.models.item import Item, item_ratings
from app.forms.list_forms import ItemForm

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

items_bp = Blueprint("items", __name__, url_prefix="/items")

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return "." in filename and filename.rsplit(
        ".", 1)[1].lower() in ALLOWED_EXTENSIONS


@items_bp.route("/add/<int:list_id>", methods=["GET", "POST"])
@login_required
def add_item(list_id):
    form = ItemForm()
    if form.validate_on_submit():
        image_url = "uploads/default_thumbnail.png"  # Imagen por defecto

        if form.image.data:
            file = form.image.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                        filename)
                file.save(filepath)

                # Guardar la ruta relativa en la base de datos
                image_url = f"uploads/{filename}"

        new_item = Item(content=form.content.data,
                        list_id=list_id,
                        image_url=image_url)
        db.session.add(new_item)
        db.session.commit()
        current_user.add_score(0.1)
        flash("Ítem agregado con éxito!", "success")
        return redirect(url_for("lists.view_list", list_id=list_id))

    flash("Error al añadir el ítem. Verifica los datos.", "danger")
    return redirect(url_for("lists.view_list", list_id=list_id))


@items_bp.route("/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)

    if form.validate_on_submit():
        item.content = form.content.data

        if form.image.data:
            file = form.image.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                        filename)
                file.save(filepath)

                item.image_url = f"uploads/{filename}"  # Guardamos solo la ruta relativa

        db.session.commit()
        flash("Ítem actualizado con éxito!", "success")
        return redirect(url_for("lists.view_list", list_id=item.list.id))

    return render_template("items/edit_item.html", form=form, item=item)


@items_bp.route("/rate/<int:item_id>", methods=["POST"])
@login_required
def rate_item(item_id):
    item = Item.query.get_or_404(item_id)
    rating = request.form.get("rating", type=int)

    if not (0 <= rating <= 5):
        flash("El rating debe estar entre 0 y 5 estrellas", "danger")
        return redirect(url_for("lists.view_list", list_id=item.list_id))

    existing_rating = db.session.query(item_ratings).filter_by(
        user_id=current_user.id, item_id=item_id).first()

    if existing_rating:
        db.session.execute(item_ratings.update().where(
            (item_ratings.c.user_id == current_user.id)
            & (item_ratings.c.item_id == item_id)).values(rating=rating))
    else:
        current_user.add_score(0.1)
        db.session.execute(item_ratings.insert().values(
            user_id=current_user.id, item_id=item_id, rating=rating))

        if item.list.owner.id != current_user.id:
            item.list.owner.add_notification("rating", f"{current_user.username} valoró un ítem en tu lista '{item.list.name}'.")


    db.session.commit()
    flash("Calificación guardada con éxito!", "success")
    return redirect(url_for("lists.view_list", list_id=item.list_id))


@items_bp.route("/delete/<int:item_id>", methods=["GET", "POST"])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)

    if item.list.owner.id != current_user.id:
        flash("No tienes permiso para eliminar este ítem", "danger")
        return redirect(url_for("lists.dashboard"))

    if request.method == "POST":
        db.session.delete(item)
        db.session.commit()
        flash("Ítem eliminado", "danger")
        return redirect(url_for("lists.view_list", list_id=item.list.id))

    return render_template("items/delete_item.html", item=item, form=form)
