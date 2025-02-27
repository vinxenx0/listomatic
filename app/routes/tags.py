from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models.tag import Tag
from app.forms.tag_forms import TagForm

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")

@tags_bp.route("/manage", methods=["GET", "POST"])
@login_required
def manage_tags():
    form = TagForm()
    if form.validate_on_submit():
        new_tag = Tag(name=form.name.data)
        db.session.add(new_tag)
        db.session.commit()
        flash("Etiqueta creada", "success")
        return redirect(url_for("tags.manage_tags"))

    tags = Tag.query.all()
    return render_template("tags/manage_tags.html", form=form, tags=tags)

@tags_bp.route("/delete/<int:tag_id>")
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash("Etiqueta eliminada", "danger")
    return redirect(url_for("tags.manage_tags"))
