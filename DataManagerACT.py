import logging
from database import database
from datetime import datetime, date, timedelta
from Generated.DatabaseClasses import *


class DataManagerACT:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)

        self.db_manager = db_manager

    def current_day_functions(self):
        try:
            self.logger.info("RUNNING CURRENT DAY FUNCTIONS FOR ACT")
            self.update_act_player_score()
            self.get_act_lineup()
            self.db_manager.commit()
        except Exception as e:
            self.logger.exception("ERROR IN ACT CURRENT DAY")
            raise e

    def update_act_player_score(self):
        self.logger.info("Attempting to update actual player scores in LP_INPUTS")
        select_lp_inputs_to_update = database.entity(LpInputs)
        select_lp_inputs_to_update.add_where(LpInputs.act_fd_score, None)
        lp_inputs_to_update = self.db_manager.select_all(select_lp_inputs_to_update)
        self.logger.info("Found " +
                         str(len(lp_inputs_to_update)) +
                         " LP INPUTS to be updated")
        for update_row in lp_inputs_to_update:
            if update_row.get(LpInputs.fd_position) == 'G':
                act_stats_table = GoalieStats
            else:
                act_stats_table = PlayerStats
            select_act_stats = database.entity(act_stats_table)
            select_act_stats.add_where(act_stats_table.game_id, update_row.get(LpInputs.nhl_game_id))
            select_act_stats.add_where(act_stats_table.player_id, update_row.get(LpInputs.nhl_player_id))
            act_stats = self.db_manager.select_single(select_act_stats)
            if act_stats is not None:
                self.logger.debug("Found actual stats for PLAYER with ID " +
                                  str(update_row.get(LpInputs.nhl_player_id)) +
                                  " and GAME with ID " +
                                  str(update_row.get(LpInputs.nhl_game_id)))
                if act_stats_table == GoalieStats:
                    fd_score = self.get_goalie_score(act_stats)
                else:
                    fd_score = self.get_player_score(act_stats)
            else:
                self.logger.info("Could not find actual stats so updating to FD SCORE of 0.0")
                fd_score = 0.0
            update_row.set(LpInputs.act_fd_score, fd_score)
        self.db_manager.update(lp_inputs_to_update, commit=False)

    def get_act_lineup(self):
        self.logger.info("Attempting to get actual lineup from yesterday's predicted lineup")
        select_slate = database.entity(FdSlates)
        slate_date = date.today()
        slate_date -= timedelta(days=1)
        self.logger.debug("Using " + str(slate_date) + " to find slate")
        select_slate.add_where(slate_date)
        slate = self.db_manager.select_single(select_slate)
        select_lp_lineup = database.entity(LpLineups)
        select_lp_lineup.add_where(LpLineups.slate_id, slate.get(FdSlates.id))
        select_lp_lineup.add_where(LpLineups.is_actual, False)
        select_lp_lineup.add_where(LpLineups.is_perfect, False)
        select_lp_lineup.add_where(LpLineups.user_modified, False)
        lp_lineup = self.db_manager.select_single(select_lp_lineup)
        if lp_lineup is not None:
            self.logger.debug("Found yesterday's predicted LP_LINEUP with ID " +
                              str(lp_lineup.get(LpLineups.id)))
            select_lp_players = database.entity(LpLineupPlayers)
            select_lp_players.add_where(LpLineupPlayers.lineup_id, lp_lineup.get(LpLineups.id))
            lp_players = self.db_manager.select_all(select_lp_players)
            self.logger.debug("Found " + str(len(lp_players)) + "LP_LINEUP_PLAYERS from yesterday's lineup")
            select_lp_inputs = database.entity(LpInputs)
            select_lp_inputs.add_where(LpInputs.slate_id, slate.get(FdSlates.id))
            lp_inputs = self.db_manager.select_all(select_lp_inputs)
            self.logger.debug("Found " + str(len(lp_inputs)) + " LP_INPUTS for consideration")
            insert_lp_players = []
            total_points = 0.0
            for lp_player in lp_players:
                for lp_input in lp_inputs:
                    if lp_input.get(LpInputs.nhl_player_id) == lp_player.get(LpLineupPlayers.nhl_id):
                        self.logger.debug("Adding PLAYER with ID " +
                                          str(lp_player.get(LpLineupPlayers.nhl_id)) +
                                          " to list of LP PLAYERS to insert")
                        insert_lp_player = database.entity(LpLineupPlayers)
                        insert_lp_player.set(LpLineupPlayers.nhl_id, lp_player.get(LpLineupPlayers.nhl_id))
                        insert_lp_player.set(LpLineupPlayers.position, lp_player.get(LpLineupPlayers.position))
                        insert_lp_player.set(LpLineupPlayers.salary, lp_player.get(LpLineupPlayers.salary))
                        insert_lp_player.set(LpLineupPlayers.fd_score, lp_input.get(LpInputs.act_fd_score))
                        insert_lp_players.append(insert_lp_player)
                        total_points += lp_input.get(LpInputs.act_fd_score)
                        break

            insert_lp_lineup = database.entity(LpLineups)
            insert_lp_lineup.set(LpLineups.slate_id, lp_lineup.get(LpLineups.slate_id))
            insert_lp_lineup.set(LpLineups.is_actual, True)
            insert_lp_lineup.set(LpLineups.is_perfect, False)
            insert_lp_lineup.set(LpLineups.result, None)
            insert_lp_lineup.set(LpLineups.total_salary, lp_lineup.get(LpLineups.total_salary))
            insert_lp_lineup.set(LpLineups.total_points, total_points)
            insert_lp_lineup.set(LpLineups.date_time, datetime.now())
            lineup_id = self.db_manager.insert(insert_lp_lineup, commit=False)

            for insert_lp_player in insert_lp_players:
                insert_lp_player.set(LpLineupPlayers.lineup_id, lineup_id)

            self.db_manager.insert(insert_lp_players, commit=False)
        else:
            self.logger.warning("Could not find yesterdays predicted LP_LINEUP for SLATE with ID" +
                                str(slate.get(FdSlates.id)))

    def get_player_score(self, act_stats):
        self.logger.debug("Attempting to get PLAYER SCORE for PLAYER with ID " +
                          str(act_stats.get(PlayerStats.player_id)) +
                          " and GAME with ID " +
                          str(act_stats.get(PlayerStats.game_id)))
        score = 0.0
        score += act_stats.get(PlayerStats.goals) * 12
        score += act_stats.get(PlayerStats.assists) * 8
        score += act_stats.get(PlayerStats.ppg) * 0.5
        score += act_stats.get(PlayerStats.ppa) * 0.5
        score += act_stats.get(PlayerStats.shg) * 2
        score += act_stats.get(PlayerStats.sha) * 2
        score += act_stats.get(PlayerStats.shots) * 1.6
        score += act_stats.get(PlayerStats.blocked) * 1.6
        self.logger.debug("Calculated PLAYER SCORE of " +
                          str(score) +
                          " for PLAYER with ID " +
                          str(act_stats.get(PlayerStats.player_id)))
        return score

    def get_goalie_score(self, act_stats):
        self.logger.debug("Attempting to get GOALIE SCORE for GOALIE with ID " +
                          str(act_stats.get(GoalieStats.player_id)) +
                          " and GAME with ID " +
                          str(act_stats.get(GoalieStats.game_id)))
        score = 0.0
        is_win = act_stats.get(GoalieStats.decision) == 'W'
        total_shots = act_stats.get(GoalieStats.total_shots)
        total_saves = act_stats.get(GoalieStats.total_saves)
        is_shutout = total_shots == total_saves
        ga = total_shots - total_saves
        score += is_win * 12
        score += is_shutout * 8
        score += total_saves * 0.8
        score -= ga * 4
        self.logger.debug("Calculated GOALIE SCORE of " + str(score))
        return score
