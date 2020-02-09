import Logger
from DataManager import DataManager

logger_name = "Predictor"
Logger.setup(logger_name)
manager = DataManager(logger_name)
manager.current_day_functions()

# https://www.nhl.com/news/nhl-lineups-goalie-starters-fantasy-projections-injury-updates/c-278165828