import os
import smtplib
import threading
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")


# ---------- CORE EMAIL FUNCTION ----------
def _send(receiver, subject, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = receiver

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, receiver, msg.as_string())
        server.quit()

    except Exception as e:
        print("Email Error:", e)


# ---------- NON-BLOCKING EMAIL ----------
def send_email_async(receiver, subject, message):
    thread = threading.Thread(target=_send, args=(receiver, subject, message))
    thread.start()


# ---------- TEMPLATES ----------
def email_new_complaint(name, sid, dept, category, issue, desc):
    subject = "📢 New Complaint Submitted"
    message = f"""
New Complaint Received

Student Name : {name}
Student ID   : {sid}
Department   : {dept}

Category     : {category}
Issue        : {issue}
Description  : {desc}
"""
    send_email_async(ADMIN_EMAIL, subject, message)


def email_status_update(receiver, cid, status):
    subject = "✅ Complaint Status Updated"
    message = f"""
Your complaint ID {cid} status is now: {status}

Thank you for using Smart Campus Care 🎓
"""
    send_email_async(receiver, subject, message)