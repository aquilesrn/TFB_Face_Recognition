# Utiliza la imagen base de Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Instalar curl
RUN apt-get update && apt-get install -y curl    

# Copia los archivos requirements.txt al contenedor
COPY requirements.txt requirements.txt

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de la carpeta actual al directorio de trabajo del contenedor
COPY . .

# Expone el puerto 8000 para la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]