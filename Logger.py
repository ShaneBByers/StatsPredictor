import logging
import Constants
import smtplib
from datetime import datetime
from email.message import EmailMessage
from logging.handlers import RotatingFileHandler, BufferingHandler


class Logger:

    def __init__(self):
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)
        self.simple_format = logging.Formatter(
            '%(asctime)s - ' +
            '%(levelname)s - ' +
            '%(message)s - ' +
            'FILE: %(filename)s - ' +
            'FUNC: %(funcName)s - ' +
            'LINE: %(lineno)d')

    def add_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(self.simple_format)
        self.log.addHandler(console_handler)

    def add_file_handler(self, log_file_name, log_level):
        file_handler = RotatingFileHandler(log_file_name, maxBytes=10485760, backupCount=10)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(self.simple_format)
        self.log.addHandler(file_handler)

    def add_email_handler(self):
        email_handler = BufferingSMTPHandler(Constants.LOGGING_EMAIL_HOST,
                                             Constants.LOGGING_EMAIL_USERNAME,
                                             Constants.LOGGING_EMAIL_PASSWORD,
                                             Constants.LOGGING_FROM_EMAIL,
                                             Constants.LOGGING_TO_EMAIL,
                                             "PREDICTOR WARNINGS/ERRORS",
                                             100)
        email_handler.setLevel(logging.WARNING)
        email_handler.setFormatter(self.simple_format)
        self.log.addHandler(email_handler)

    def setup_local(self):
        self.add_console_handler()
        self.add_file_handler("WARNING.log", logging.WARNING)

    def setup_current_day(self):
        self.add_file_handler("DEBUG.log", logging.DEBUG)
        self.add_file_handler("WARNING.log", logging.WARNING)
        self.add_email_handler()

    def setup_testing(self):
        self.add_console_handler()
        self.add_email_handler()


class BufferingSMTPHandler(BufferingHandler):

    def __init__(self, host, username, password, from_email, to_email, subject, capacity):
        BufferingHandler.__init__(self, capacity)
        self.host = host
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_email = to_email
        self.subject = subject
        self.buffer = []

    def flush(self):
        if len(self.buffer) > 0:
            msg = EmailMessage()
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Subject'] = self.subject
            msg['Date'] = datetime.now()
            content = ""
            for record in self.buffer:
                content += self.format(record) + "\n"
            msg.set_content(content)
            server = smtplib.SMTP(self.host)
            server.ehlo()
            server.starttls(*(self.username, self.password))
            server.ehlo()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            self.buffer = []
