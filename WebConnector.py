import requests
import logging
from collections import OrderedDict


class WebConnector:

    def __init__(self, logger_name, base_url):
        self.logger = logging.getLogger(logger_name)
        self.base_url = base_url
        self.__last = ""

    def get(self, append_string):
        self.__last = self.base_url + append_string
        self.logger.info("Attempting request of: " + self.__last)
        return requests.get(self.__last).json(object_pairs_hook=OrderedDict)

    @property
    def last(self):
        return self.__last
