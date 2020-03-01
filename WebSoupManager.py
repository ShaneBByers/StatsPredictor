import logging
import urllib.request
from bs4 import BeautifulSoup


class WebSoupManager:

    def __init__(self, url_path):
        self.logger = logging.getLogger(__name__)
        self.url_path = url_path

    def get_soup(self):
        self.logger.debug("Attempting request of " + self.url_path)
        fp = urllib.request.urlopen(self.url_path)
        self.logger.info("Successfully requested: " + self.url_path)
        html_bytes = fp.read()
        html_str = html_bytes.decode("utf8")
        soup = BeautifulSoup(html_str, "html.parser")
        self.logger.debug("Successfully created soup.")
        return soup
