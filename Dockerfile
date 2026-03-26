FROM python:3.11-slim

WORKDIR /app

# copiar los requerimientos primero para aprovechar la cache de docker
COPY requirements.txt .

# instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# copiar todo el proyecto
COPY . .

# puerto de la aplicacion
EXPOSE 8000

# comando para iniciar la aplicacion
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
