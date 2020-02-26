import logging
from WebConnector import WebConnector


class WebManager:

    def __init__(self, base_url):
        self.logger = logging.getLogger(__name__)
        self.connector = WebConnector(base_url)

    def get(self, append_string):
        values = self.connector.get(append_string)
        self.logger.info("Get request: " + self.connector.last)
        return values
