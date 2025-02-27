from app import db
from app.models.list import List

print(db.engine.table_names())  # Ver qué tablas existen en la DB
