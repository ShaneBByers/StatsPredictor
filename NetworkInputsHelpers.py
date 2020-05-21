import logging
from Generated.DatabaseClasses import *


class NetworkInputsHelpers:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.current_season = None
        self.player_dict = {}

        self.method_list = []

    # def avg_amt_this_season(self, player_stats, player_stats_var):
    #     all_prev_player_stats = self.get_prev_player_stats(player_stats)
    #     total_amt = 0.0
    #     for single_stats in all_prev_player_stats:
    #         single_amt = single_stats.get(player_stats_var)
    #         if single_amt is not None:
    #             total_amt += single_amt
    #     if len(all_prev_player_stats) > 0:
    #         avg_amt = total_amt / len(all_prev_player_stats)
    #     else:
    #         avg_amt = 0.0
    #     return avg_amt
    #
    # def get_prev_player_stats(self, player_stats, reverse_order=True):
    #     self.logger.debug("Getting previous player stats for season for GAME_ID " +
    #                       str(player_stats.get(PlayerStats.game_id)) +
    #                       " and PLAYER_ID " +
    #                       str(player_stats.get(PlayerStats.player_id)))
    #     game_id = player_stats.get(PlayerStats.game_id)
    #     first_game_id = int(game_id / 1000000)
    #     first_game_id = first_game_id * 1000000
    #     select_prev_player_stats = database.entity(PlayerStats)
    #     select_prev_player_stats.add_where(PlayerStats.player_id, player_stats.get(PlayerStats.player_id))
    #     select_prev_player_stats.add_where(PlayerStats.game_id, first_game_id, ">=")
    #     select_prev_player_stats.add_where(PlayerStats.game_id, player_stats.get(PlayerStats.game_id), "<")
    #     select_prev_player_stats.add_order_by(PlayerStats.game_id, not reverse_order)
    #     prev_player_stats = self.db_manager.select_all(select_prev_player_stats)
    #     self.logger.debug("Got " +
    #                       str(len(prev_player_stats)) +
    #                       " previous PLAYER_STATS for this season to consider")
    #     return prev_player_stats

    def get_avg_player_stat_from_season(self, player_stats, specific_stat):
        player_id = player_stats.get(PlayerStats.player_id)
        if player_id in self.player_dict:
            total_stat = 0.0
            for single_player_stats in self.player_dict[player_id]:
                single_amt = single_player_stats.get(specific_stat)
                if single_amt is None:
                    single_amt = 0.0
                total_stat += single_amt
            total_len = len(self.player_dict[player_id])
            if total_len > 0:
                return total_stat / total_len
        return 0.0

    def get_specific_player_stat_from_games_ago(self, player_stats, specific_stat, games_ago):
        player_id = player_stats.get(PlayerStats.player_id)
        if player_id in self.player_dict and len(self.player_dict[player_id]) >= games_ago:
            return self.player_dict[player_id][games_ago-1].get(specific_stat)
        return 0.0

    def add_player_stats_to_dict(self, player_stats):
        player_id = player_stats.get(PlayerStats.player_id)
        if player_id not in self.player_dict:
            self.player_dict[player_id] = [player_stats]
        else:
            self.player_dict[player_id].insert(0, player_stats)
