from Logger import Logger
from DataManager import DataManager

logger = Logger()
logger.setup_current_day()

manager = DataManager()
manager.current_day_functions()
