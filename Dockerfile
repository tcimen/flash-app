FROM python:3.9-slim

# Gerekli sistem paketlerini ve ODBC sürücüsünü yükleyin.
RUN apt-get update && \
    apt-get install -y curl telnet unixodbc-dev gcc build-essential unixodbc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Microsoft ODBC Driver'ları zaten yüklü olduğundan ek bir şey yapmaya gerek yok

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]