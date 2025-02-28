import os
from app import create_app
from config import config_dict

# Obtener el entorno de ejecución (por defecto "development")
env = os.getenv("FLASK_ENV", "development")
app = create_app()
app.config.from_object(config_dict[env])

if __name__ == "__main__":
    if app.config.get("USE_SSL", False):  # Solo usar SSL en desarrollo si está activado
        ssl_context = (
            app.config.get("SSL_CERT_PATH"),
            app.config.get("SSL_KEY_PATH")
        )
        app.run(debug=app.config["DEBUG"], host="0.0.0.0", ssl_context=ssl_context)
    else:
        app.run(debug=app.config["DEBUG"], host="0.0.0.0")
