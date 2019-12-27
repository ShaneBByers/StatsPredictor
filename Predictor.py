import Logger
from DataManager import DataManager

logger_name = "Predictor"
Logger.setup(logger_name)
manager = DataManager(logger_name)
manager.insert_player_stats()
