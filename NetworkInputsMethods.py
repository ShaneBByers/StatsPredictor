import logging
from NetworkInputsHelpers import NetworkInputsHelpers
from database import database
from Generated.DatabaseClasses import *


class NetworkInputsMethods:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager

        self.helpers = NetworkInputsHelpers(db_manager)

        self.method_list = []

        self.initialize_method_list()

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
        self.logger.debug("Attempting to get PLAYER_INPUTS for PLAYER_STATS with GAME_ID " +
                          str(player_stats.get(PlayerStats.game_id)) +
                          " and PLAYER_ID " +
                          str(player_stats.get(PlayerStats.player_id)))
        for player_param in player_params:
            if not player_param.get(NnPlayerParams.is_done) and player_param.get(NnPlayerParams.id) <= 8:
                insert_player_input = database.entity(NnPlayerInputs)
                insert_player_input.set(NnPlayerInputs.game_id, player_stats.get(PlayerStats.game_id))
                insert_player_input.set(NnPlayerInputs.player_id, player_stats.get(PlayerStats.player_id))
                insert_player_input.set(NnPlayerInputs.param_id, player_param.get(NnPlayerParams.id))
                method_index = player_param.get(NnPlayerParams.id) - 1
                method = self.method_list[method_index]
                input_value = method(player_stats)
                insert_player_input.set(NnPlayerInputs.input_value, input_value)
                self.db_manager.insert(insert_player_input, commit=False)

    def avg_goals_this_season(self, player_stats):
        self.logger.info("GETTING AVG_GOALS_THIS_SEASON")
        avg_goals = self.helpers.avg_amt_this_season(player_stats, PlayerStats.goals)
        return avg_goals

    def avg_assists_this_season(self, player_stats):
        self.logger.info("GETTING AVG_ASSISTS_THIS_SEASON")
        avg_assists = self.helpers.avg_amt_this_season(player_stats, PlayerStats.assists)
        return avg_assists

    def avg_shots_this_season(self, player_stats):
        self.logger.info("GETTING AVG_SHOTS_THIS_SEASON")
        avg_shots = self.helpers.avg_amt_this_season(player_stats, PlayerStats.shots)
        return avg_shots

    def avg_ppg_this_season(self, player_stats):
        self.logger.info("GETTING AVG_PPG_THIS_SEASON")
        avg_ppg = self.helpers.avg_amt_this_season(player_stats, PlayerStats.ppg)
        return avg_ppg

    def avg_ppa_this_season(self, player_stats):
        self.logger.info("GETTING AVG_PPA_THIS_SEASON")
        avg_ppa = self.helpers.avg_amt_this_season(player_stats, PlayerStats.ppa)
        return avg_ppa

    def avg_shg_this_season(self, player_stats):
        self.logger.info("GETTING AVG_SHG_THIS_SEASON")
        avg_shg = self.helpers.avg_amt_this_season(player_stats, PlayerStats.shg)
        return avg_shg

    def avg_sha_this_season(self, player_stats):
        self.logger.info("GETTING AVG_SHA_THIS_SEASON")
        avg_sha = self.helpers.avg_amt_this_season(player_stats, PlayerStats.sha)
        return avg_sha

    def avg_blocked_this_season(self, player_stats):
        self.logger.info("GETTING AVG_BLOCKED_THIS_SEASON")
        avg_blocked = self.helpers.avg_amt_this_season(player_stats, PlayerStats.blocked)
        return avg_blocked

    def goals_1_game_ago(self, player_stats):
        return

    def goals_2_games_ago(self, player_stats):
        return

    def goals_3_games_ago(self, player_stats):
        return

    def goals_4_games_ago(self, player_stats):
        return

    def goals_5_games_ago(self, player_stats):
        return

    def goals_6_games_ago(self, player_stats):
        return

    def goals_7_games_ago(self, player_stats):
        return

    def goals_8_games_ago(self, player_stats):
        return

    def goals_9_games_ago(self, player_stats):
        return

    def goals_10_games_ago(self, player_stats):
        return

    def assists_1_game_ago(self, player_stats):
        return

    def assists_2_games_ago(self, player_stats):
        return

    def assists_3_games_ago(self, player_stats):
        return

    def assists_4_games_ago(self, player_stats):
        return

    def assists_5_games_ago(self, player_stats):
        return

    def assists_6_games_ago(self, player_stats):
        return

    def assists_7_games_ago(self, player_stats):
        return

    def assists_8_games_ago(self, player_stats):
        return

    def assists_9_games_ago(self, player_stats):
        return

    def assists_10_games_ago(self, player_stats):
        return

    def shots_1_game_ago(self, player_stats):
        return

    def shots_2_games_ago(self, player_stats):
        return

    def shots_3_games_ago(self, player_stats):
        return

    def shots_4_games_ago(self, player_stats):
        return

    def shots_5_games_ago(self, player_stats):
        return

    def shots_6_games_ago(self, player_stats):
        return

    def shots_7_games_ago(self, player_stats):
        return

    def shots_8_games_ago(self, player_stats):
        return

    def shots_9_games_ago(self, player_stats):
        return

    def shots_10_games_ago(self, player_stats):
        return

    def ppg_1_game_ago(self, player_stats):
        return

    def ppg_2_games_ago(self, player_stats):
        return

    def ppg_3_games_ago(self, player_stats):
        return

    def ppg_4_games_ago(self, player_stats):
        return

    def ppg_5_games_ago(self, player_stats):
        return

    def ppg_6_games_ago(self, player_stats):
        return

    def ppg_7_games_ago(self, player_stats):
        return

    def ppg_8_games_ago(self, player_stats):
        return

    def ppg_9_games_ago(self, player_stats):
        return

    def ppg_10_games_ago(self, player_stats):
        return

    def ppa_1_game_ago(self, player_stats):
        return

    def ppa_2_games_ago(self, player_stats):
        return

    def ppa_3_games_ago(self, player_stats):
        return

    def ppa_4_games_ago(self, player_stats):
        return

    def ppa_5_games_ago(self, player_stats):
        return

    def ppa_6_games_ago(self, player_stats):
        return

    def ppa_7_games_ago(self, player_stats):
        return

    def ppa_8_games_ago(self, player_stats):
        return

    def ppa_9_games_ago(self, player_stats):
        return

    def ppa_10_games_ago(self, player_stats):
        return

    def shg_1_game_ago(self, player_stats):
        return

    def shg_2_games_ago(self, player_stats):
        return

    def shg_3_games_ago(self, player_stats):
        return

    def shg_4_games_ago(self, player_stats):
        return

    def shg_5_games_ago(self, player_stats):
        return

    def shg_6_games_ago(self, player_stats):
        return

    def shg_7_games_ago(self, player_stats):
        return

    def shg_8_games_ago(self, player_stats):
        return

    def shg_9_games_ago(self, player_stats):
        return

    def shg_10_games_ago(self, player_stats):
        return

    def sha_1_game_ago(self, player_stats):
        return

    def sha_2_games_ago(self, player_stats):
        return

    def sha_3_games_ago(self, player_stats):
        return

    def sha_4_games_ago(self, player_stats):
        return

    def sha_5_games_ago(self, player_stats):
        return

    def sha_6_games_ago(self, player_stats):
        return

    def sha_7_games_ago(self, player_stats):
        return

    def sha_8_games_ago(self, player_stats):
        return

    def sha_9_games_ago(self, player_stats):
        return

    def sha_10_games_ago(self, player_stats):
        return

    def blocked_1_game_ago(self, player_stats):
        return

    def blocked_2_games_ago(self, player_stats):
        return

    def blocked_3_games_ago(self, player_stats):
        return

    def blocked_4_games_ago(self, player_stats):
        return

    def blocked_5_games_ago(self, player_stats):
        return

    def blocked_6_games_ago(self, player_stats):
        return

    def blocked_7_games_ago(self, player_stats):
        return

    def blocked_8_games_ago(self, player_stats):
        return

    def blocked_9_games_ago(self, player_stats):
        return

    def blocked_10_games_ago(self, player_stats):
        return

    def is_defense(self, player_stats):
        return

    def is_center(self, player_stats):
        return

    def is_left_winger(self, player_stats):
        return

    def is_right_winger(self, player_stats):
        return

    def shoots_right(self, player_stats):
        return

    def player_age(self, player_stats):
        return

    def player_height(self, player_stats):
        return

    def player_weight(self, player_stats):
        return

    def season_years_ago(self, player_stats):
        return

    def is_divisional_game(self, player_stats):
        return

    def is_conference_game(self, player_stats):
        return

    def is_home_game(self, player_stats):
        return

    def game_start_hour(self, player_stats):
        return

    def player_season_game_count(self, player_stats):
        return

    def team_season_game_count(self, player_stats):
        return

    def team_games_since_last_player_game(self, player_stats):
        return

    def player_season_games_on_team(self, player_stats):
        return

    def player_season_avg_pim(self, player_stats):
        return

    def player_season_total_plus_minus(self, player_stats):
        return

    def player_season_avg_takeaways(self, player_stats):
        return

    def player_season_avg_giveaways(self, player_stats):
        return

    def player_season_avg_toi(self, player_stats):
        return

    def player_season_avg_pp_toi(self, player_stats):
        return

    def player_season_avg_sh_toi(self, player_stats):
        return

    def player_season_avg_even_toi(self, player_stats):
        return

    def player_season_avg_toi_last_10_games(self, player_stats):
        return

    def player_season_avg_pp_toi_last_10_games(self, player_stats):
        return

    def player_season_avg_sh_toi_last_10_games(self, player_stats):
        return

    def player_season_avg_even_toi_last_10_games(self, player_stats):
        return

    def team_season_avg_goals(self, player_stats):
        return

    def team_season_avg_shots(self, player_stats):
        return

    def team_season_avg_pps(self, player_stats):
        return

    def team_season_avg_ppgs(self, player_stats):
        return

    def team_season_avg_pim(self, player_stats):
        return

    def team_season_avg_blocked(self, player_stats):
        return

    def team_season_avg_takeaways(self, player_stats):
        return

    def team_season_avg_giveaways(self, player_stats):
        return

    def team_season_avg_hits(self, player_stats):
        return

    def opp_team_season_avg_pps(self, player_stats):
        return

    def opp_team_season_avg_pim(self, player_stats):
        return

    def opp_team_season_avg_blocked(self, player_stats):
        return

    def opp_team_season_avg_hits(self, player_stats):
        return

    def opp_goalie_season_avg_sa(self, player_stats):
        return

    def opp_goalie_season_avg_even_sa(self, player_stats):
        return

    def opp_goalie_season_avg_pp_sa(self, player_stats):
        return

    def opp_goalie_season_avg_sh_sa(self, player_stats):
        return

    def opp_goalie_season_avg_saves(self, player_stats):
        return

    def opp_goalie_season_avg_even_saves(self, player_stats):
        return

    def opp_goalie_season_avg_pp_saves(self, player_stats):
        return

    def opp_goalie_season_avg_sh_saves(self, player_stats):
        return

    def opp_goalie_season_avg_save_percent(self, player_stats):
        return

    def opp_goalie_season_avg_even_save_percent(self, player_stats):
        return

    def opp_goalie_season_avg_pp_save_percent(self, player_stats):
        return

    def opp_goalie_season_avg_sh_save_percent(self, player_stats):
        return

    def opp_goalie_season_game_count(self, player_stats):
        return

    def opp_goalie_season_avg_toi(self, player_stats):
        return

    def days_since_last_team_game(self, player_stats):
        return

    def days_since_last_opp_team_game(self, player_stats):
        return

    def days_since_last_player_game(self, player_stats):
        return

    def days_since_last_opp_goalie_game(self, player_stats):
        return

    def is_playoff_game(self, player_stats):
        return

    def playoff_round(self, player_stats):
        return

    def team_vs_opp_last_5_seasons_game_count(self, player_stats):
        return

    def team_vs_opp_last_5_seasons_avg_goals(self, player_stats):
        return

    def team_vs_opp_last_5_seasons_avg_pps(self, player_stats):
        return

    def team_vs_opp_last_5_seasons_avg_opp_pps(self, player_stats):
        return

    def team_vs_opp_last_5_seasons_avg_player_goals(self, player_stats):
        return

    def team_vs_opp_last_5_seasons_avg_player_assists(self, player_stats):
        return

    def player_season_goals_per_toi_100_secs(self, player_stats):
        return

    def player_season_goals_per_pp_toi_100_secs(self, player_stats):
        return

    def opp_team_season_avg_ga(self, player_stats):
        return

    def opp_team_season_avg_pks(self, player_stats):
        return

    def opp_team_season_avg_sa(self, player_stats):
        return

    def initialize_method_list(self):
        self.method_list = [self.avg_goals_this_season,
                            self.avg_assists_this_season,
                            self.avg_shots_this_season,
                            self.avg_ppg_this_season,
                            self.avg_ppa_this_season,
                            self.avg_shg_this_season,
                            self.avg_sha_this_season,
                            self.avg_blocked_this_season,
                            self.goals_1_game_ago,
                            self.goals_2_games_ago,
                            self.goals_3_games_ago,
                            self.goals_4_games_ago,
                            self.goals_5_games_ago,
                            self.goals_6_games_ago,
                            self.goals_7_games_ago,
                            self.goals_8_games_ago,
                            self.goals_9_games_ago,
                            self.goals_10_games_ago,
                            self.assists_1_game_ago,
                            self.assists_2_games_ago,
                            self.assists_3_games_ago,
                            self.assists_4_games_ago,
                            self.assists_5_games_ago,
                            self.assists_6_games_ago,
                            self.assists_7_games_ago,
                            self.assists_8_games_ago,
                            self.assists_9_games_ago,
                            self.assists_10_games_ago,
                            self.shots_1_game_ago,
                            self.shots_2_games_ago,
                            self.shots_3_games_ago,
                            self.shots_4_games_ago,
                            self.shots_5_games_ago,
                            self.shots_6_games_ago,
                            self.shots_7_games_ago,
                            self.shots_8_games_ago,
                            self.shots_9_games_ago,
                            self.shots_10_games_ago,
                            self.ppg_1_game_ago,
                            self.ppg_2_games_ago,
                            self.ppg_3_games_ago,
                            self.ppg_4_games_ago,
                            self.ppg_5_games_ago,
                            self.ppg_6_games_ago,
                            self.ppg_7_games_ago,
                            self.ppg_8_games_ago,
                            self.ppg_9_games_ago,
                            self.ppg_10_games_ago,
                            self.ppa_1_game_ago,
                            self.ppa_2_games_ago,
                            self.ppa_3_games_ago,
                            self.ppa_4_games_ago,
                            self.ppa_5_games_ago,
                            self.ppa_6_games_ago,
                            self.ppa_7_games_ago,
                            self.ppa_8_games_ago,
                            self.ppa_9_games_ago,
                            self.ppa_10_games_ago,
                            self.shg_1_game_ago,
                            self.shg_2_games_ago,
                            self.shg_3_games_ago,
                            self.shg_4_games_ago,
                            self.shg_5_games_ago,
                            self.shg_6_games_ago,
                            self.shg_7_games_ago,
                            self.shg_8_games_ago,
                            self.shg_9_games_ago,
                            self.shg_10_games_ago,
                            self.sha_1_game_ago,
                            self.sha_2_games_ago,
                            self.sha_3_games_ago,
                            self.sha_4_games_ago,
                            self.sha_5_games_ago,
                            self.sha_6_games_ago,
                            self.sha_7_games_ago,
                            self.sha_8_games_ago,
                            self.sha_9_games_ago,
                            self.sha_10_games_ago,
                            self.blocked_1_game_ago,
                            self.blocked_2_games_ago,
                            self.blocked_3_games_ago,
                            self.blocked_4_games_ago,
                            self.blocked_5_games_ago,
                            self.blocked_6_games_ago,
                            self.blocked_7_games_ago,
                            self.blocked_8_games_ago,
                            self.blocked_9_games_ago,
                            self.blocked_10_games_ago,
                            self.is_defense,
                            self.is_center,
                            self.is_left_winger,
                            self.is_right_winger,
                            self.shoots_right,
                            self.player_age,
                            self.player_height,
                            self.player_weight,
                            self.season_years_ago,
                            self.is_divisional_game,
                            self.is_conference_game,
                            self.is_home_game,
                            self.game_start_hour,
                            self.player_season_game_count,
                            self.team_season_game_count,
                            self.team_games_since_last_player_game,
                            self.player_season_games_on_team,
                            self.player_season_avg_pim,
                            self.player_season_total_plus_minus,
                            self.player_season_avg_takeaways,
                            self.player_season_avg_giveaways,
                            self.player_season_avg_toi,
                            self.player_season_avg_pp_toi,
                            self.player_season_avg_sh_toi,
                            self.player_season_avg_even_toi,
                            self.player_season_avg_toi_last_10_games,
                            self.player_season_avg_pp_toi_last_10_games,
                            self.player_season_avg_sh_toi_last_10_games,
                            self.player_season_avg_even_toi_last_10_games,
                            self.team_season_avg_goals,
                            self.team_season_avg_shots,
                            self.team_season_avg_pps,
                            self.team_season_avg_ppgs,
                            self.team_season_avg_pim,
                            self.team_season_avg_blocked,
                            self.team_season_avg_takeaways,
                            self.team_season_avg_giveaways,
                            self.team_season_avg_hits,
                            self.opp_team_season_avg_pps,
                            self.opp_team_season_avg_pim,
                            self.opp_team_season_avg_blocked,
                            self.opp_team_season_avg_hits,
                            self.opp_goalie_season_avg_sa,
                            self.opp_goalie_season_avg_even_sa,
                            self.opp_goalie_season_avg_pp_sa,
                            self.opp_goalie_season_avg_sh_sa,
                            self.opp_goalie_season_avg_saves,
                            self.opp_goalie_season_avg_even_saves,
                            self.opp_goalie_season_avg_pp_saves,
                            self.opp_goalie_season_avg_sh_saves,
                            self.opp_goalie_season_avg_save_percent,
                            self.opp_goalie_season_avg_even_save_percent,
                            self.opp_goalie_season_avg_pp_save_percent,
                            self.opp_goalie_season_avg_sh_save_percent,
                            self.opp_goalie_season_game_count,
                            self.opp_goalie_season_avg_toi,
                            self.days_since_last_team_game,
                            self.days_since_last_opp_team_game,
                            self.days_since_last_player_game,
                            self.days_since_last_opp_goalie_game,
                            self.is_playoff_game,
                            self.playoff_round,
                            self.team_vs_opp_last_5_seasons_game_count,
                            self.team_vs_opp_last_5_seasons_avg_goals,
                            self.team_vs_opp_last_5_seasons_avg_pps,
                            self.team_vs_opp_last_5_seasons_avg_opp_pps,
                            self.team_vs_opp_last_5_seasons_avg_player_goals,
                            self.team_vs_opp_last_5_seasons_avg_player_assists,
                            self.player_season_goals_per_toi_100_secs,
                            self.player_season_goals_per_pp_toi_100_secs,
                            self.opp_team_season_avg_ga,
                            self.opp_team_season_avg_pks,
                            self.opp_team_season_avg_sa]
