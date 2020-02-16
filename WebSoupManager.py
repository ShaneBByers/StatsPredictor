import logging
import urllib.request
# import ssl
from bs4 import BeautifulSoup


class WebSoupManager:

    def __init__(self, logger_name, url_path):
        self.logger = logging.getLogger(logger_name)
        self.url_path = url_path

    def get_soup(self):
        # ssl._create_default_https_context = ssl._create_unverified_context
        fp = urllib.request.urlopen(self.url_path)
        html_bytes = fp.read()
        html_str = html_bytes.decode("utf8")
        soup = BeautifulSoup(html_str, "html.parser")
        return soup
