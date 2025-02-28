sudo apt install python-pytest

# gunicorn
pip install flask flask-sqlalchemy flask-login flask-wtf flask-migrate bootstrap-flask email_validator pytest
pip install python-dotenv
pip install pymysql


flask db init    # Solo si es la primera vez
flask db migrate -m "Actualización de modelos"
flask db upgrade


python -m flask db migrate -m "Actualización de modelos"
python -m flask db upgrade

############ buena

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

copiar .env.example .env

db_init.sh 
(arreglar lo del Text)
flask db upgrade
flask init-db
