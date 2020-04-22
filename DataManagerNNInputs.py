import logging
import pickle
import Constants
from database import database
from Generated.DatabaseClasses import *


class DataManagerNNInputs:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)

        self.db_manager = db_manager

        self.method_list = [self.avg_goals_this_season,
                            self.avg_assists_this_season,
                            self.avg_shots_this_season,
                            self.avg_ppg_this_season,
                            self.avg_ppa_this_season,
                            self.avg_shg_this_season,
                            self.avg_sha_this_season,
                            self.avg_blocked_this_season]

    def pickle_inputs(self):
        pickle_file = open(Constants.NN_INPUTS_FILENAME, 'wb+')

        input_array = []
        select_games = database.entity(Games)
        select_games.add_where(Games.is_home, True)
        games = self.db_manager.select_all(select_games)
        for game in games:
            select_player_stats = database.entity(PlayerStats)
            select_player_stats.add_where(PlayerStats.game_id, game.get(Games.id))
            single_game_all_player_stats = self.db_manager.select_all(select_player_stats)
            for single_player_stats in single_game_all_player_stats:
                select_player_inputs = database.entity(NnPlayerInputs)
                select_player_inputs.add_where(NnPlayerInputs.game_id, game.get(Games.id))
                select_player_inputs.add_where(NnPlayerInputs.player_id, single_player_stats.get(PlayerStats.player_id))
                player_inputs = self.db_manager.select_all(select_player_inputs)
                player_input_array = []
                for player_input in player_inputs:
                    player_input_array.append(player_input.get(NnPlayerInputs.input_value))
                blocked = single_player_stats.get(PlayerStats.blocked)
                if blocked is None:
                    blocked = 0.0
                adjusted_blocked = blocked / 10.0
                player_output_array = [single_player_stats.get(PlayerStats.goals),
                                       single_player_stats.get(PlayerStats.assists),
                                       single_player_stats.get(PlayerStats.shots) / 10.0,
                                       single_player_stats.get(PlayerStats.ppg),
                                       single_player_stats.get(PlayerStats.ppa),
                                       single_player_stats.get(PlayerStats.shg),
                                       single_player_stats.get(PlayerStats.sha),
                                       adjusted_blocked]
                input_array.append((player_input_array, player_output_array))

        pickle.dump(input_array, pickle_file)
        pickle_file.close()
        self.logger.info("Player input array created.")

    def insert_player_inputs(self):
        self.logger.info("Inserting all player inputs")
        select_player_params = database.entity(NnPlayerParams)
        player_params = self.db_manager.select_all(select_player_params)
        self.logger.debug("Found " +
                          str(len(player_params)) +
                          " PLAYER_PARAMS to consider")
        for player_param in player_params:
            method_index = player_param.get(NnPlayerParams.id) - 1
            method = self.method_list[method_index]
            db_method_name = player_param.get(NnPlayerParams.method_name)
            self.logger.debug("Checking if PLAYER_PARAM with METHOD_INDEX " +
                              str(method_index) +
                              " is the method with METHOD_NAME " +
                              db_method_name)
            if method.__name__ != db_method_name:
                self.logger.error("Param methods in DB do not match methods in DataManagerNN")
                return

        select_games = database.entity(Games)
        select_games.add_where(Games.is_home, True)
        games = self.db_manager.select_all(select_games)
        self.logger.debug("Got " +
                          str(len(games)) +
                          " GAMES to consider")

        for game in games:
            select_player_stats = database.entity(PlayerStats)
            select_player_stats.add_where(PlayerStats.game_id, game.get(Games.id))
            single_game_all_player_stats = self.db_manager.select_all(select_player_stats)
            self.logger.debug("Got " +
                              str(len(single_game_all_player_stats)) +
                              " PLAYER_STATS for GAME with ID " +
                              str(game.get(Games.id)) +
                              " to consider")
            for single_player_stats in single_game_all_player_stats:
                self.insert_player_inputs_for_player_stats(single_player_stats, player_params)
        self.db_manager.commit()

    def insert_player_inputs_for_player_stats(self, player_stats, player_params):
        self.logger.info("Attempting to get PLAYER_INPUTS for PLAYER_STATS with GAME_ID " +
                         str(player_stats.get(PlayerStats.player_id)) +
                         " and PLAYER_ID " +
                         str(player_stats.get(PlayerStats.game_id)))
        for player_param in player_params:
            if not player_param.get(NnPlayerParams.is_done):
                insert_player_input = database.entity(NnPlayerInputs)
                insert_player_input.set(NnPlayerInputs.game_id, player_stats.get(PlayerStats.game_id))
                insert_player_input.set(NnPlayerInputs.player_id, player_stats.get(PlayerStats.player_id))
                insert_player_input.set(NnPlayerInputs.param_id, player_param.get(NnPlayerParams.id))
                method_index = player_param.get(NnPlayerParams.id) - 1
                method = self.method_list[method_index]
                input_value = method(player_stats)
                insert_player_input.set(NnPlayerInputs.input_value, input_value)
                self.db_manager.insert(insert_player_input, commit=False)

    def avg_amt_this_season(self, player_stats, player_stats_var):
        all_prev_player_stats = self.get_prev_player_stats(player_stats)
        total_amt = 0.0
        for single_stats in all_prev_player_stats:
            single_amt = single_stats.get(player_stats_var)
            if single_amt is not None:
                total_amt += single_amt
        if len(all_prev_player_stats) > 0:
            avg_amt = total_amt / len(all_prev_player_stats)
        else:
            avg_amt = 0.0
        return avg_amt

    def avg_goals_this_season(self, player_stats):
        self.logger.info("GETTING AVG_GOALS_THIS_SEASON")
        avg_goals = self.avg_amt_this_season(player_stats, PlayerStats.goals)
        return avg_goals

    def avg_assists_this_season(self, player_stats):
        self.logger.info("GETTING AVG_ASSISTS_THIS_SEASON")
        avg_assists = self.avg_amt_this_season(player_stats, PlayerStats.assists)
        return avg_assists

    def avg_shots_this_season(self, player_stats):
        self.logger.info("GETTING AVG_SHOTS_THIS_SEASON")
        avg_shots = self.avg_amt_this_season(player_stats, PlayerStats.shots)
        adjusted_avg_shots = avg_shots / 10.0
        return adjusted_avg_shots

    def avg_ppg_this_season(self, player_stats):
        self.logger.info("GETTING AVG_PPG_THIS_SEASON")
        avg_ppg = self.avg_amt_this_season(player_stats, PlayerStats.ppg)
        return avg_ppg

    def avg_ppa_this_season(self, player_stats):
        self.logger.info("GETTING AVG_PPA_THIS_SEASON")
        avg_ppa = self.avg_amt_this_season(player_stats, PlayerStats.ppa)
        return avg_ppa

    def avg_shg_this_season(self, player_stats):
        self.logger.info("GETTING AVG_SHG_THIS_SEASON")
        avg_shg = self.avg_amt_this_season(player_stats, PlayerStats.shg)
        return avg_shg

    def avg_sha_this_season(self, player_stats):
        self.logger.info("GETTING AVG_SHA_THIS_SEASON")
        avg_sha = self.avg_amt_this_season(player_stats, PlayerStats.sha)
        return avg_sha

    def avg_blocked_this_season(self, player_stats):
        self.logger.info("GETTING AVG_BLOCKED_THIS_SEASON")
        avg_blocked = self.avg_amt_this_season(player_stats, PlayerStats.blocked)
        adjusted_avg_blocked = avg_blocked / 10.0
        return adjusted_avg_blocked

    def get_prev_player_stats(self, player_stats, reverse_order=True):
        self.logger.debug("Getting previous player stats for season for GAME_ID " +
                          str(player_stats.get(PlayerStats.game_id)) +
                          " and PLAYER_ID " +
                          str(player_stats.get(PlayerStats.player_id)))
        game_id = player_stats.get(PlayerStats.game_id)
        first_game_id = int(game_id / 1000000)
        first_game_id = first_game_id * 1000000
        select_prev_player_stats = database.entity(PlayerStats)
        select_prev_player_stats.add_where(PlayerStats.player_id, player_stats.get(PlayerStats.player_id))
        select_prev_player_stats.add_where(PlayerStats.game_id, first_game_id, ">=")
        select_prev_player_stats.add_where(PlayerStats.game_id, player_stats.get(PlayerStats.game_id), "<")
        select_prev_player_stats.add_order_by(PlayerStats.game_id, not reverse_order)
        prev_player_stats = self.db_manager.select_all(select_prev_player_stats)
        self.logger.debug("Got " +
                          str(len(prev_player_stats)) +
                          " previous PLAYER_STATS for this season to consider")
        return prev_player_stats
