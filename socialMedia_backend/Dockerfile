# Python 3.11 Slim imajı
FROM python:3.11-slim

# Çalıştırma dizinini belirle
WORKDIR /app

# Sistem kütüphanelerini güncelle ve gereken temel araçları kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Önce hafif CPU versiyolu PyTorch'u kur (gereksiz CUDA gigabytelarını indirmez, süper hızlı derlenir!)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Gereksinim dosyasını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kaynak kodunu kopyala
COPY . .

# Cloud Run için standart port tanımı (Varsayılan 8080, ortam değişkeninden override edilebilir)
ENV PORT=8080
EXPOSE 8080

# Sunucuyu başlat (Uvicorn)
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
