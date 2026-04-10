import os, smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

MAIL_PROVIDER = os.getenv("MAIL_PROVIDER", "console")
MAIL_FROM = os.getenv("MAIL_FROM", "Viewz Studio OS <no-reply@localhost>")
MAILTRAP_SMTP_HOST = os.getenv("MAILTRAP_SMTP_HOST", "sandbox.smtp.mailtrap.io")
MAILTRAP_SMTP_PORT = int(os.getenv("MAILTRAP_SMTP_PORT", "2525"))
MAILTRAP_SMTP_USER = os.getenv("MAILTRAP_SMTP_USER")
MAILTRAP_SMTP_PASS = os.getenv("MAILTRAP_SMTP_PASS")

def _send_mailtrap(to_email: str, subject: str, html: str):
    name, addr = (MAIL_FROM.split("<")[0].strip(), MAIL_FROM.split("<")[-1].strip(">").strip())
    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((name, addr))
    msg["To"] = to_email
    
    with smtplib.SMTP(MAILTRAP_SMTP_HOST, MAILTRAP_SMTP_PORT) as s:
        s.login(MAILTRAP_SMTP_USER, MAILTRAP_SMTP_PASS)
        s.sendmail(addr, [to_email], msg.as_string())

def send_email(to_email: str, subject: str, html: str):
    if MAIL_PROVIDER == "mailtrap":
        _send_mailtrap(to_email, subject, html)
        return True
    print("=== EMAIL (DEV) ===")
    print("TO:", to_email)
    print("SUBJECT:", subject)
    print(html)
    print("===================")
    return True

