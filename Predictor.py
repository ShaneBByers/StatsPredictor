from Logger import Logger
from DataManager import DataManager

logger = Logger()
logger.setup_local()

manager = DataManager()
manager.manager_nhl.full_season("20052006")
