# Usar imagen oficial de Python ligera
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias primero para cachear esta capa
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto que usará Azure
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["python", "run.py"]
