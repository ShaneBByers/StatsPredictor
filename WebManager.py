import logging
import requests
from collections import OrderedDict


class WebManager:

    def __init__(self, base_url):
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url
        self.__last = ""

    def get(self, append_string):
        self.__last = self.base_url + append_string
        self.logger.debug("Attempting request of: " + self.__last)
        values = requests.get(self.__last).json(object_pairs_hook=OrderedDict)
        self.logger.info("Successfully requested: " + self.__last)
        return values
