# 🔹 Usar Python 3.9 como base
FROM python:3.9

# 🔹 Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# 🔹 Copiar los archivos de la aplicación al contenedor
COPY . /app

# 🔹 Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 🔹 Exponer el puerto 5000 para Flask
EXPOSE 5000

# desarrolllo
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

# produccion
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
