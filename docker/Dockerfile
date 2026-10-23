FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances minimales pour PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Exécution directe du script principal
CMD ["python"]
#CMD ["python", "main.py"]
