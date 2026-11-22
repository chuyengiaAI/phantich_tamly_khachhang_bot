FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file phụ thuộc và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn và dữ liệu hội thoại
COPY . .

# Chạy Bot
CMD ["python", "main.py"]
