sudo apt install python-pytest

pip install python-dotenv
# pymysql
# gunicorn
pip install flask flask-sqlalchemy flask-login flask-wtf flask-migrate bootstrap-flask email_validator pytest


flask db init    # Solo si es la primera vez
flask db migrate -m "Actualización de modelos"
flask db upgrade


python -m flask db migrate -m "Actualización de modelos"
python -m flask db upgrade


python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

db_init.sh 
(arreglar lo del Text)
flask db upgrade
flask init-db
