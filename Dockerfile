FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema para WeasyPrint
RUN apt-get update && apt-get install -y \
    gcc \
    libpango1.0-dev \
    libharfbuzz-dev \
    libffi-dev \
    libcairo2-dev \
    libgdk-pixbuf-xlib-2.0-dev \
    libglib2.0-dev \
    libgtk-3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY backend/ .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["sh", "-c", "python init_db.py && gunicorn app:app -c gunicorn.conf.py"]
