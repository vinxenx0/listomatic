from datetime import datetime
import os
from flask import Blueprint, abort, flash, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
from app import db
from flask import current_app
from app.models.category import Category
from app.models.list import List, likes_table
from app.models.item import item_ratings
from app.models.tag import Tag
from app.forms.list_forms import ListForm
from app.forms.list_forms import ItemForm

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return "." in filename and filename.rsplit(
        ".", 1)[1].lower() in ALLOWED_EXTENSIONS


lists_bp = Blueprint("lists", __name__, url_prefix="/lists")


@lists_bp.route("/dashboard")
@login_required
def dashboard():
    user_lists = List.query.filter_by(user_id=current_user.id).all()

    category_counts = {category.name: 0 for category in Category.get_all()}
    for category_name, count in (db.session.query(
            List.category, func.count(
                List.id)).filter(List.user_id == current_user.id).group_by(
                    List.category).all()):
        category_counts[category_name] = count

    return render_template("lists/dashboard.html",
                           lists=user_lists,
                           category_counts=category_counts)


@lists_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_list():
    form = ListForm()
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

        category = Category.query.get(
            form.category.data
        )  # ✅ Obtener el objeto Category en lugar de usar un int

        if not category:
            flash(
                "Categoría inválida. Por favor, selecciona una categoría válida.",
                "danger")
            return render_template("lists/create_list.html", form=form)

        new_list = List(
            name=form.name.data,
            is_public=form.is_public.data,
            category=category,  # ✅ Ahora se asigna un objeto `Category`
            icon=form.icon.data,
            user_id=current_user.id)

        db.session.add(new_list)

        # Procesar etiquetas
        if form.tags.data is None or not isinstance(form.tags.data, str):
            form.tags.data = ""

        tag_names = [
            tag.strip().lower() for tag in form.tags.data.split(",")
            if tag.strip()
        ]

        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.flush()
            new_list.tags.append(tag)

        db.session.commit()
        flash("Lista creada exitosamente", "success")
        return redirect(url_for("lists.dashboard"))

    return render_template("lists/create_list.html", form=form)


@lists_bp.route("/edit/<int:list_id>", methods=["GET", "POST"])
@login_required
def edit_list(list_id):
    list_obj = List.query.get_or_404(list_id)
    if list_obj.user_id != current_user.id:
        abort(403)

    form = ListForm(obj=list_obj)

    # Cargar etiquetas actuales en el formulario
    if request.method == "GET":
        form.tags.data = ", ".join(tag.name for tag in list_obj.tags)

    if form.validate_on_submit():
        list_obj.name = form.name.data
        list_obj.category = form.category.data
        list_obj.is_public = form.is_public.data
        list_obj.icon = form.icon.data

        # Si el usuario sube una nueva imagen, la guardamos
        if form.image.data:
            file = form.image.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"],
                                        filename)
                file.save(filepath)

                list_obj.image_url = f"uploads/{filename}"  # Guardamos solo la ruta relativa

        # Actualizar etiquetas
        list_obj.tags = []
        if form.tags.data is None or not isinstance(form.tags.data, str):
            form.tags.data = ""

        tag_names = [
            tag.strip().lower() for tag in form.tags.data.split(",")
            if tag.strip()
        ]

        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.flush()
            list_obj.tags.append(tag)

        list_obj.updated_at = datetime.utcnow()

        db.session.commit()
        flash("Lista actualizada con éxito", "success")
        return redirect(url_for("lists.dashboard"))

    return render_template("lists/edit_list.html",
                           form=form,
                           list_obj=list_obj)


@lists_bp.route("/delete/<int:list_id>", methods=["GET", "POST"])
@login_required
def delete_list(list_id):
    list_obj = List.query.get_or_404(list_id)
    if list_obj.user_id != current_user.id:
        abort(403)

    if request.method == "POST":
        db.session.delete(list_obj)
        db.session.commit()
        flash("Lista eliminada", "danger")
        return redirect(url_for("lists.dashboard"))

    return render_template("lists/delete_list.html", list_obj=list_obj)


@lists_bp.route("/view/<int:list_id>")
def view_list(list_id):
    list_obj = List.query.get_or_404(list_id)

    # Permitir ver la lista solo si es pública o si el usuario es el dueño
    if not list_obj.is_public and (not current_user.is_authenticated
                                   or list_obj.user_id != current_user.id):
        abort(403)

    form = ItemForm()

    category_counts = {category.name: 0 for category in Category.get_all()}
    for category_name, count in (db.session.query(
            List.category, func.count(
                List.id)).filter(List.user_id == current_user.id).group_by(
                    List.category).all()):
        category_counts[category_name] = count

    # Obtener los ratings de cada ítem en esta lista hechos por el usuario actual
    user_ratings = {}
    if current_user.is_authenticated:
        user_ratings = {
            item_id: rating
            for item_id, rating in db.session.query(
                item_ratings.c.item_id, item_ratings.c.rating).filter_by(
                    user_id=current_user.id).all()
        }

    return render_template("lists/view_list.html",
                           list_obj=list_obj,
                           form=form,
                           item_ratings=user_ratings,
                           category_counts=category_counts)


@lists_bp.route("/like/<int:list_id>/<string:action>", methods=["POST"])
@login_required
def like_list(list_id, action):
    """Permite a los usuarios dar like o dislike a una lista."""
    list_obj = List.query.get_or_404(list_id)

    if not list_obj.is_public:
        flash("No puedes interactuar con una lista privada", "danger")
        return redirect(url_for("lists.view_list", list_id=list_id))

    is_like = action == "like"

    # Verificar si el usuario ya tiene un registro en likes_table
    existing_like = db.session.query(likes_table).filter_by(
        user_id=current_user.id, list_id=list_id).first()

    if existing_like:
        # Si el usuario ya dio like/dislike y selecciona la misma acción, eliminarlo
        if existing_like.is_like == is_like:
            db.session.execute(likes_table.delete().where(
                (likes_table.c.user_id == current_user.id)
                & (likes_table.c.list_id == list_id)))
            db.session.commit()
            flash("Tu voto ha sido eliminado", "info")
        else:
            # Si cambia de like a dislike o viceversa, actualizar
            db.session.execute(likes_table.update().where(
                (likes_table.c.user_id == current_user.id)
                & (likes_table.c.list_id == list_id)).values(is_like=is_like))
            db.session.commit()
            flash("Tu voto ha sido actualizado", "success")
    else:
        # Insertar nuevo like o dislike
        db.session.execute(likes_table.insert().values(user_id=current_user.id,
                                                       list_id=list_id,
                                                       is_like=is_like))
        db.session.commit()
        flash("Tu voto ha sido registrado", "success")

    return redirect(url_for("lists.view_list", list_id=list_id))


@lists_bp.route("/category/<int:category_id>")
def lists_by_category(category_id):
    """Filtrar listas por categoría."""
    category = Category.query.get_or_404(category_id)
    filtered_lists = List.query.filter_by(category_id=category.id).all()
    return render_template("lists/category.html",
                           lists=filtered_lists,
                           category=category)


@lists_bp.route("/tag/<string:tag_name>")
def lists_by_tag(tag_name):
    """Filtrar listas por etiqueta."""
    from app.models.tag import Tag
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    return render_template("lists/tag.html", lists=tag.lists, tag=tag)
