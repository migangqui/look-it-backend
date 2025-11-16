# Usa una imagen base de Python oficial, ligera (slim) y adecuada
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los requisitos e instálalos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente de la aplicación
COPY . .

# Define la variable de entorno que Cloud Run usará para el puerto
ENV PORT 8080

# Comando para iniciar el servidor Uvicorn
# 'main:app' es (nombre_archivo_python:nombre_objeto_FastAPI)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT