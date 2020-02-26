import os
from Logger import Logger
from DataManager import DataManager

logger = Logger()
logger.setup_local()

file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "Generated/DatabaseClasses.py")
manager = DataManager(all_active=False)
manager.update_classes_file(file_path)
