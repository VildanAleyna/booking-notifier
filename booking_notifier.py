import os
import imaplib
import email
import re
import requests

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Telegram'a mesaj gönderme fonksiyonu
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    r = requests.post(url, data=data)
    print(" Telegram gönderim sonucu:", r.status_code, r.text)  # 🔹 LOG


# Mail kontrol fonksiyonu
def check_mail():
    print(" Gmail'e bağlanılıyor...")  # 🔹 LOG
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_PASS)
    print(" Gmail giriş başarılı")  # 🔹 LOG
    mail.select("inbox")  # Gelen kutusunu seç

    # Yeni gelen mailleri ara
    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()
    print(f" Okunmamış mail sayısı: {len(email_ids)}")  # 🔹 LOG

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg["subject"]
                sender = msg["from"]

                print(f" Yeni mail -> Konu: {subject}, Gönderen: {sender}")  # 🔹 LOG

                # Mailin gövdesini al
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type in ["text/plain", "text/html"]:
                            try:
                                body = part.get_payload(decode=True).decode()
                                break
                            except Exception:
                                pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode()
                    except Exception:
                        body = ""

                # Sadece booking mailleri için
                if sender and "booking.com" in sender.lower():
                    print(" Booking mail bulundu!")  # 🔹 LOG
                    urls = re.findall(r'https?://\S+', body)
                    first_url = urls[0] if urls else "link bulunamadı"

                    # Telegram mesajı
                    message = f"Yeni Rezervasyonunuz bulunuyor.!! Konu: {subject}\nDetaylar: {first_url}"
                    send_telegram_message(message)

    mail.logout()
    print(" Mail kontrol tamamlandı.")  # 🔹 LOG


if __name__ == "__main__":
    # İlk test için Telegram'a direkt mesaj at
    print(" Test mesajı gönderiliyor...")  # 🔹 LOG
    send_telegram_message(" Test mesajı çalışıyor mu?")

    # Daha sonra gerçek mailleri kontrol etmek için:
    # check_mail()
