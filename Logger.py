import logging
import Constants
from logging.handlers import RotatingFileHandler, SMTPHandler, MemoryHandler


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
        email_handler = SMTPHandler(Constants.LOGGING_EMAIL_HOST,
                                    Constants.LOGGING_FROM_EMAIL,
                                    [Constants.LOGGING_TO_EMAIL],
                                    "PREDICTOR WARNING/ERROR",
                                    credentials=(Constants.LOGGING_EMAIL_USERNAME,
                                                 Constants.LOGGING_EMAIL_PASSWORD))
        email_handler.setFormatter(self.simple_format)
        memory_handler = MemoryHandler(100, target=email_handler)
        memory_handler.setLevel(logging.WARNING)
        self.log.addHandler(memory_handler)

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
