FROM python:3.11-slim

# システムライブラリのインストール
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Node.js (LTS v20) のインストール
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

WORKDIR /workspace

# Pythonライブラリのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# コンテナ起動時のデフォルトコマンド（必要に応じて）
# CMD ["python", "main.py"]