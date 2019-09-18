import logging
import Constants
from database import database
from WebManager import WebManager
from Generated.DatabaseClasses import *


class DataManager:

    def __init__(self, logger_name, db=True, web=True):
        self.logger = logging.getLogger(logger_name)

        if db:
            self.db_manager = database.connect(logger_name,
                                               Constants.DB_HOST,
                                               Constants.DB_USERNAME,
                                               Constants.DB_PASSWORD,
                                               Constants.DB_NAME)
        else:
            self.db_manager = None

        if web:
            self.web_manager = WebManager(logger_name,
                                          Constants.WEB_BASE_URL)
        else:
            self.web_manager = None

    def update_classes_file(self, file_name):
        self.db_manager.update_classes_file(file_name)

    def get_teams(self):
        teams = self.web_manager.get_teams()
        return True
