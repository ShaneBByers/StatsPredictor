import logging
from WebConnector import WebConnector


class WebManager:

    def __init__(self, logger_name, base_url):
        self.logger = logging.getLogger(logger_name)
        self.connector = WebConnector(logger_name, base_url)

    # def get_teams(self):
    #     teams = self.connector.get("teams")
    #     self.logger.info("Get teams request: " + self.connector.last)
    #     return teams

    def get(self, append_string):
        values = self.connector.get(append_string)
        self.logger.info("Get request: " + self.connector.last)
        return values
