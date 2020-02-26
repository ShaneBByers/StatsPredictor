from Logger import Logger
from DataManager import DataManager

logger = Logger()
logger.setup_local()

manager = DataManager()
manager.current_day_functions()
