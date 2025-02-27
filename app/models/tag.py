from app import db

list_tags = db.Table(
    "list_tags",
    db.Column("list_id", db.Integer, db.ForeignKey("list.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True)
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

