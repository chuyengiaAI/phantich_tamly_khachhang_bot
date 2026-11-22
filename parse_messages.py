import os
import re
import glob
from bs4 import BeautifulSoup

def clean_sender(sender: str) -> str:
    sender = sender.strip()
    if "Đào Hồng Lâu Mộng" in sender or "CSKH" in sender:
        return "CSKH"
    if "佳怡" in sender:
        return "GiaiDi"
    if len(sender) > 20:
        return sender[:20]
    return sender

def parse_all_messages():
    folder_path = "đoạn hội thoại"
    files = ["messages.html"] + [f"messages{i}.html" for i in range(2, 60)]
    valid_files = [os.path.join(folder_path, f) for f in files if os.path.exists(os.path.join(folder_path, f))]
    
    print(f"Tìm thấy {len(valid_files)} file HTML hội thoại.")
    
    output_lines = []
    current_sender = "Unknown"
    current_date = ""
    total_messages = 0

    for file_path in valid_files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            
            history_div = soup.find("div", class_="history")
            if not history_div:
                continue

            for elem in history_div.find_all("div", class_="message"):
                classes = elem.get("class", [])
                
                # Cập nhật ngày
                if "service" in classes:
                    date_body = elem.find("div", class_="body details")
                    if date_body:
                        current_date = date_body.get_text(strip=True)
                        output_lines.append(f"\n--- {current_date} ---")
                    continue
                
                # Tin nhắn người dùng
                if "default" in classes:
                    from_name_div = elem.find("div", class_="from_name")
                    if from_name_div:
                        current_sender = clean_sender(from_name_div.get_text(strip=True))
                    
                    text_div = elem.find("div", class_="text")
                    if text_div:
                        for br in text_div.find_all("br"):
                            br.replace_with("\n")
                        text_content = text_div.get_text().strip()
                        
                        # Loại bỏ các thông báo hệ thống tự động
                        if text_content and not text_content.startswith("Not included, change data exporting"):
                            total_messages += 1
                            output_lines.append(f"{current_sender}: {text_content}")

    output_text = "\n".join(output_lines)
    
    output_file = "extracted_conversation.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_text)
        
    print(f"\n✅ Đã trích xuất thành công {total_messages} tin nhắn!")
    print(f"📄 Đã lưu vào file '{output_file}'. Kích thước: {os.path.getsize(output_file) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    parse_all_messages()
