rm -rf instance/*
rm -rf migrations

flask db init
flask db migrate -m "migrate"
flask db upgrade
# fflask init-db
