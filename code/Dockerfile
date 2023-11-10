# Use la imagen base de Python con Alpine Linux
FROM python:3.7-alpine

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requisitos y instalar las dependencias
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Gunicorn
RUN pip install gunicorn

# Copiar el resto de los archivos del código fuente
COPY . .

# Definir la variable de entorno para la aplicación Flask
ENV FLASK_APP=app.py

# Exponer el puerto que Gunicorn usará
EXPOSE 5000

# Ejecutar Gunicorn y servir la aplicación Flask
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
