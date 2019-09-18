import requests


class WebConnector:

    def __init__(self, base_url):
        self.base_url = base_url
        self.__last = ""

    def get(self, append_string):
        self.__last = self.base_url + append_string
        return requests.get(self.__last).json()

    @property
    def last(self):
        return self.__last
