# 🤖 Telegram Bot Gemini AI

Bot Telegram thông minh tích hợp **Google Gemini API** (`gemini-2.5-flash`), hỗ trợ trả lời bất kỳ câu hỏi nào của người dùng một cách chính xác dựa trên thông tin có sẵn (Knowledge Base) hoặc kiến thức chung.

---

## 📋 Tính năng nổi bật

- ⚡ **Phản hồi siêu tốc & chính xác**: Sử dụng mô hình `gemini-2.5-flash` mới nhất từ Google.
- 📚 **Thông tin có sẵn (Knowledge Base)**: Đọc dữ liệu từ file `knowledge.txt` để trả lời chính xác các thông tin về sản phẩm, dịch vụ, quy định, FAQ,... của bạn.
- 💬 **Ghi nhớ ngữ cảnh hội thoại**: Bot tự động nhớ lịch sử trò chuyện để trả lời các câu hỏi tiếp nối.
- 🔄 **Nạp lại dữ liệu tức thì (`/reload`)**: Cập nhật thông tin mới trong `knowledge.txt` mà không cần khởi động lại Server.
- 🧹 **Xóa bộ nhớ (`/reset`)**: Cho phép người dùng làm mới cuộc trò chuyện bất cứ lúc nào.

---

## 🛠️ Hướng dẫn cài đặt & Khởi chạy

### Bước 1: Tạo Telegram Bot Token
1. Mở ứng dụng Telegram, tìm kiếm bot `@BotFather`.
2. Gửi lệnh `/newbot` và đặt tên, username cho bot của bạn.
3. Sao chép chuỗi **HTTP API Token** (ví dụ: `789101112:AAE...`).

### Bước 2: Lấy Gemini API Key
1. Truy cập [Google AI Studio](https://aistudio.google.com/).
2. Đăng nhập bằng tài khoản Google.
3. Chọn **Get API key** ➔ **Create API key** và sao chép API Key.

### Bước 3: Cấu hình File `.env`
Tạo file `.env` trong thư mục project (có thể sao chép từ `.env.example`):

```env
TELEGRAM_BOT_TOKEN=điền_token_telegram_tại_đây
GEMINI_API_KEY=điền_gemini_api_key_tại_đây
```

### Bước 4: Nhập dữ liệu thông tin có sẵn
Mở file `knowledge.txt` và nhập nội dung/kiến thức mà bạn muốn Bot nắm rõ (ví dụ: thông tin cửa hàng, bảng giá, quy định, dịch vụ,...).

### Bước 5: Cài đặt thư viện & Khởi chạy Bot

Mở Terminal trong thư mục dự án và chạy:

```bash
# Cài đặt các thư viện cần thiết
python -m pip install -r requirements.txt

# Khởi chạy Telegram Bot
python main.py
```

---

## 📱 Hướng dẫn sử dụng các lệnh Telegram Bot

| Lệnh | Chức năng |
| :--- | :--- |
| `/start` | Khởi động bot và hiển thị lời chào |
| `/help` | Xem hướng dẫn sử dụng bot |
| `/reset` | Xóa bộ nhớ trò chuyện cũ để bắt đầu chủ đề mới |
| `/reload` | Nạp lại kiến thức mới từ `knowledge.txt` |
