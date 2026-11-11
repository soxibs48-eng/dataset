# Python bazaviy obrazi
FROM python:3.11-slim

WORKDIR /app

# Kutubxonalarni o'rnatish
RUN pip install --no-cache-dir pandas scikit-learn kagglehub joblib

# Loyiha fayllarini ko'chirish
COPY . /app

# Portlar (Veb-sayt: 8000, REST API: 5000)
EXPOSE 8000 5000

# Veb-serverni ishga tushirish
CMD ["python", "server.py"]

