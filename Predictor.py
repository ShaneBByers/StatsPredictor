import Logger
from DataManager import DataManager

logger_name = "Predictor"
Logger.setup(logger_name)
manager = DataManager(logger_name)
# manager.get_soup_data()
# manager.get_pred_player_stats()
# manager.calc_lineup()
# manager.manager_nhl.insert_player_stats(current_season=False,
#                                         season_id=20192020,
#                                         is_goalie=True)
manager.manager_fd.current_day_functions()
