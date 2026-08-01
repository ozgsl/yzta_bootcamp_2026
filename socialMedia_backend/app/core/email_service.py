import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def send_otp_email(to_email: str, subject: str, body: str) -> bool:
    """
    SMTP sunucusu yapılandırılmışsa mail gönderir.
    Yapılandırılmamışsa, test için konsola yazdırır.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"\n[{'='*40}]", flush=True)
        print(f"MOCK EMAIL SENT TO: {to_email}", flush=True)
        print(f"SUBJECT: {subject}", flush=True)
        print(f"BODY:\n{body}", flush=True)
        print(f"[{'='*40}]\n", flush=True)
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USER, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def generate_otp() -> str:
    return str(random.randint(100000, 999999))
