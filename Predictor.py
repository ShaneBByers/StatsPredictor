import Logger
from DataManager import DataManager

logger_name = "Predictor"
Logger.setup(logger_name)
manager = DataManager(logger_name)
manager.full_season("20192020")
