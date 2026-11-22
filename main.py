import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from google import genai
from google.genai import types

# Cấu hình logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Handler cho Render Health Check (Port scan)."""
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - Bot is running")

    def log_message(self, format, *args):
        pass  # Tắt log HTTP của health check để đỡ rác log

def start_health_check_server():
    """Chạy HTTP server ngầm để Render xác nhận Port 200 OK."""
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Khởi chạy Health Check HTTP Server trên cổng {port}...")
    server.serve_forever()

# Nạp biến môi trường
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Lưu trữ phiên chat của từng người dùng
user_chats = {}
cached_system_instruction = None

def get_system_instruction() -> str:
    """Nạp toàn bộ dữ liệu hội thoại từ extracted_conversation.txt và knowledge.txt."""
    global cached_system_instruction
    if cached_system_instruction:
        return cached_system_instruction

    instruction = (
        "Bạn là một chuyên gia phân tích dữ liệu hội thoại AI thông minh, chuyên nghiệp và chính xác 100% trên Telegram.\n"
        "Nhiệm vụ của bạn là giải đáp chi tiết, sâu sắc và chính xác mọi câu hỏi của người dùng dựa trên LỊCH SỬ HỘI THOẠI ĐÃ ĐƯỢC NẠP DƯỚI ĐÂY.\n"
        "Hãy trích dẫn thời gian, tên nhân vật, nội dung cụ thể khi cần thiết để trả lời thuyết phục.\n\n"
    )
    
    # Nạp knowledge.txt nếu có
    knowledge_file = Path("knowledge.txt")
    if knowledge_file.exists():
        try:
            with open(knowledge_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    instruction += f"--- THÔNG TIN BỔ SUNG ---\n{content}\n--------------------------\n\n"
        except Exception as e:
            logger.error(f"Lỗi khi đọc knowledge.txt: {e}")

    # Nạp toàn bộ dữ liệu extracted_conversation.txt
    conv_file = Path("extracted_conversation.txt")
    if conv_file.exists():
        try:
            with open(conv_file, "r", encoding="utf-8") as f:
                conv_text = f.read().strip()
                if conv_text:
                    instruction += f"--- TOÀN BỘ LỊCH SỬ HỘI THOẠI (45,000+ TIN NHẮN) ---\n{conv_text}\n----------------------------------------------------\n"
                    logger.info(f"Đã nạp thành công lịch sử hội thoại ({len(conv_text)} ký tự).")
        except Exception as e:
            logger.error(f"Lỗi khi đọc file extracted_conversation.txt: {e}")
    else:
        logger.warning("Không tìm thấy file extracted_conversation.txt!")

    cached_system_instruction = instruction
    return cached_system_instruction

def get_or_create_user_chat(chat_id: int):
    """Tạo hoặc lấy phiên trò chuyện Gemini 3.5 Flash cho từng user."""
    if chat_id not in user_chats:
        system_instruction = get_system_instruction()
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3, # Đặt temperature thấp để câu trả lời chính xác, bám sát dữ liệu
        )
        # Sử dụng mô hình gemini-3.5-flash phân tích sâu với context khủng
        user_chats[chat_id] = client.chats.create(
            model="gemini-3.5-flash",
            config=config
        )
    return user_chats[chat_id]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /start."""
    welcome_text = (
        "👋 **Xin chào! Tôi là Bot Phân Tích & Tra Cứu Hội Thoại 24/7.**\n\n"
        "Tôi đã được nạp **toàn bộ 45.000+ tin nhắn dữ liệu hội thoại**.\n"
        "Bạn có thể hỏi tôi bất kỳ thông tin nào về các cuộc trò chuyện, nhân vật, sự kiện, thời gian hoặc chi tiết trong dữ liệu!\n\n"
        "📌 **Lệnh hỗ trợ:**\n"
        "• `/start` - Khởi động lại bot\n"
        "• `/reset` - Xóa lịch sử câu hỏi cá nhân (bắt đầu câu hỏi mới)\n"
        "• `/reload` - Nạp lại dữ liệu hội thoại từ file\n"
        "• `/help` - Xem hướng dẫn sử dụng\n\n"
        "💡 *Hãy nhập câu hỏi của bạn ngay bên dưới!*"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /help."""
    help_text = (
        "ℹ️ **Hướng dẫn đặt câu hỏi:**\n\n"
        "1. Bạn có thể hỏi chi tiết bất kỳ sự kiện, tên người, mốc thời gian hoặc nội dung nào có trong dữ liệu.\n"
        "Ví dụ:\n"
        "- *'Tóm tắt các cuộc trao đổi về công việc giữa CSKH và GiaiDi'* \n"
        "- *'Nhắc đến những khoản tiền hoặc giao dịch nào?'*\n"
        "- *'Những rủi ro hoặc kế hoạch di chuyển được thảo luận là gì?'*\n\n"
        "2. Bot sử dụng mô hình **Gemini 3.5** phân tích sâu 24/7 cho tất cả mọi người."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xóa bộ nhớ hội thoại cá nhân."""
    chat_id = update.effective_chat.id
    if chat_id in user_chats:
        del user_chats[chat_id]
    await update.message.reply_text("🧹 Đã xóa lịch sử câu hỏi cá nhân. Bạn có thể đặt câu hỏi mới!")

async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nạp lại file hội thoại."""
    global cached_system_instruction
    cached_system_instruction = None
    user_chats.clear()
    get_system_instruction()
    await update.message.reply_text("🔄 Đã nạp lại thành công toàn bộ dữ liệu hội thoại mới!", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý câu hỏi từ người dùng."""
    if not client:
        await update.message.reply_text("❌ Lỗi: Chưa cấu hình GEMINI_API_KEY trong file `.env`.")
        return

    user_text = update.message.text
    chat_id = update.effective_chat.id

    # Gửi trạng thái đang nhập (typing)
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        chat_session = get_or_create_user_chat(chat_id)
        
        # Gọi Gemini 3.5 phân tích
        response = chat_session.send_message(user_text)
        reply_content = response.text if response.text else "Xin lỗi, tôi không tìm thấy thông tin phù hợp trong dữ liệu."
        
        # Chia nhỏ tin nhắn nếu dài hơn 4000 ký tự (giới hạn tin nhắn của Telegram)
        if len(reply_content) > 4000:
            chunks = [reply_content[i:i+4000] for i in range(0, len(reply_content), 4000)]
            for chunk in chunks:
                try:
                    await update.message.reply_text(chunk, parse_mode="Markdown")
                except Exception:
                    await update.message.reply_text(chunk)
        else:
            try:
                await update.message.reply_text(reply_content, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(reply_content)

    except Exception as e:
        logger.error(f"Lỗi khi xử lý câu hỏi cho chat_id {chat_id}: {e}")
        await update.message.reply_text("⚠️ Đã xảy ra lỗi khi phân tích dữ liệu. Vui lòng thử lại câu hỏi khác.")

def main():
    """Khởi chạy Telegram Bot."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        print("❌ LỖI: Chưa thiết lập TELEGRAM_BOT_TOKEN!")
        return

    # Khởi chạy HTTP Server cho Render Health Check ngầm
    threading.Thread(target=start_health_check_server, daemon=True).start()

    # Nạp dữ liệu ban đầu
    get_system_instruction()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("reload", reload_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram Bot Gemini 3.5 đang chạy 24/7 và sẵn sàng giải đáp về dữ liệu hội thoại...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
