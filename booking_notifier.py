import os
import imaplib
import email
import re
import requests


GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def parse_booking_mail(subject, body):
    if "Yeni rezervasyon" in subject:
        rezervasyon_no = re.search(r"Booking confirmation — (\d+)", body)
        tarih = re.search(r"\d{1,2} [A-Za-zÇĞİÖŞÜçğıöşü]+ \d{4}", subject)

        oda_tipi = None
        match_oda = re.search(r"(Standart.*Oda|Çift Kişilik.*Oda|Tek Kişilik.*Oda|Family.*Room|Triple.*Room)", body, re.IGNORECASE)
        if match_oda:
            oda_tipi = match_oda.group(1)

        kisi_sayisi = None
        match_kisi = re.search(r"(\d+)\s*(yetişkin|kişi)", body, re.IGNORECASE)
        if match_kisi:
            kisi_sayisi = match_kisi.group(0)

        return (
            f" Yeni Rezervasyon!\n"
            f"Otel: Divisey Pansiyon\n"
            f"Rezervasyon No: {rezervasyon_no.group(1) if rezervasyon_no else 'bulunamadı'}\n"
            f"Tarih: {tarih.group(0) if tarih else 'bulunamadı'}\n"
            f"Oda Tipi: {oda_tipi if oda_tipi else 'belirtilmemiş'}\n"
            f"Kişi Sayısı: {kisi_sayisi if kisi_sayisi else 'belirtilmemiş'}"
        )

   
    elif "İptal edilen rezervasyon" in subject:
        rezervasyon_no = re.search(r"Cancellation — (\d+)", body)
        tarih = re.search(r"\d{1,2} [A-Za-zÇĞİÖŞÜçğıöşü]+ \d{4}", subject)

        return (
            f"❌ Rezervasyon İptal Edildi\n"
            f"Rezervasyon No: {rezervasyon_no.group(1) if rezervasyon_no else 'bulunamadı'}\n"
            f"Tarih: {tarih.group(0) if tarih else 'bulunamadı'}"
        )

    return None

def check_mail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_PASS)
    mail.select("inbox")

    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg["subject"]
                sender = msg["from"]

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

                if sender and "Vildan Aleyna Selaedin Oglou" in sender.lower():
                    parsed_message = parse_booking_mail(subject, body)
                    if parsed_message:
                        send_telegram_message(parsed_message)

    mail.logout()

if __name__ == "__main__":
    check_mail()
