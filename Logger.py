import logging
import Constants
from EmailManager import EmailManager
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
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(self.simple_format)
        self.log.addHandler(console_handler)

    def add_file_handler(self, log_file_name, log_level):
        file_handler = RotatingFileHandler(log_file_name, maxBytes=10485760, backupCount=10)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(self.simple_format)
        self.log.addHandler(file_handler)

    def add_email_handler(self):
        email_manager = EmailManager(Constants.LOGGING_EMAIL_HOST,
                                     Constants.LOGGING_EMAIL_USERNAME,
                                     Constants.LOGGING_EMAIL_PASSWORD,
                                     Constants.LOGGING_FROM_EMAIL)
        email_handler = BufferingSMTPHandler(email_manager,
                                             "PREDICTOR WARNINGS/ERRORS",
                                             100)
        email_handler.setLevel(logging.WARNING)
        email_handler.setFormatter(self.simple_format)
        self.log.addHandler(email_handler)

    def setup_local(self):
        self.add_console_handler()
        # self.add_file_handler("WARNING.log", logging.WARNING)

    def setup_current_day(self):
        self.add_file_handler("DEBUG.log", logging.DEBUG)
        self.add_file_handler("WARNING.log", logging.WARNING)
        self.add_email_handler()

    def setup_testing(self):
        self.add_console_handler()


class BufferingSMTPHandler(BufferingHandler):

    def __init__(self, email_manager, subject, capacity):
        BufferingHandler.__init__(self, capacity)
        self.email_manager = email_manager
        self.subject = subject
        self.buffer = []

    def emit(self, record):
        self.buffer.append(record)
        if self.shouldFlush(record):
            self.flush()

    def flush(self):
        if len(self.buffer) > 0:
            content = ""
            for record in self.buffer:
                content += self.format(record) + "\n"
            self.email_manager.send_email(Constants.LOGGING_TO_EMAIL,
                                          self.subject,
                                          content)
            self.buffer = []
