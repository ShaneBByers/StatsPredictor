import smtplib
from datetime import datetime
from email.message import EmailMessage


class EmailManager:

    def __init__(self, host, username, password, from_email):
        self.host = host
        self.username = username
        self.password = password
        self.from_email = from_email

    def send_email(self, to_email, subject, content):
        msg = EmailMessage()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = datetime.now()
        msg.set_content(content)
        server = smtplib.SMTP(self.host)
        server.starttls()
        server.login(self.username, self.password)
        server.send_message(msg)
        server.quit()
