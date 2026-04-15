import smtplib
from email.mime.text import MIMEText

sender = "keerthana123@gmail.com"
password = "YOUR_APP_PASSWORD"

receiver = "student@gmail.com"

msg = MIMEText("Your complaint has been resolved successfully.")
msg["Subject"] = "Complaint Update"
msg["From"] = sender
msg["To"] = receiver

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(sender, password)

server.sendmail(sender, receiver, msg.as_string())

server.quit()

print("Email sent successfully")