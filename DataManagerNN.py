import logging
from database import database
from Generated.DatabaseClasses import *


class DataManagerNN:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)

        self.db_manager = db_manager

    def current_day_functions(self):
        try:
            self.db_manager.commit()
        except Exception as e:
            self.logger.exception("ERROR IN FD CURRENT DAY")
            raise e
