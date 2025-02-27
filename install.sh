sudo apt install python-pytest


pip install flask flask-sqlalchemy flask-login flask-wtf flask-migrate bootstrap-flask email_validator pytest


flask db init    # Solo si es la primera vez
flask db migrate -m "Actualización de modelos"
flask db upgrade


python -m flask db migrate -m "Actualización de modelos"
python -m flask db upgrade
