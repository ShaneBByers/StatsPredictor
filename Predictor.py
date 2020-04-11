from Logger import Logger
from DataManager import DataManager

logger = Logger()
logger.setup_local()

manager = DataManager()
manager.manager_nn.insert_player_inputs()
