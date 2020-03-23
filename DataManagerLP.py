import logging
import Constants
from datetime import date, datetime, timedelta
from database import database
from EmailManager import EmailManager
from pulp import LpProblem, LpAffineExpression, LpVariable, LpStatus, LpMaximize, PulpSolverError
from Generated.DatabaseClasses import *


class DataManagerLP:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)

        self.db_manager = db_manager

    def current_day_functions(self):
        try:
            self.logger.info("RUNNING CURRENT DAY FUNCTIONS FOR LP")
            self.logger.info("Setting up LP input data")
            self.setup_lp_input()
            self.logger.info("Getting yesterday's actual lineup")
            self.calculate_lineup(predicted=False)
            self.logger.info("Getting today's predicted lineup")
            self.calculate_lineup(predicted=True)
            self.db_manager.commit()
        except Exception as e:
            self.logger.exception("ERROR IN LP CURRENT DAY")
            raise e

    def setup_lp_input(self):
        select_slate = database.entity(FdSlates)
        slate_date = date.today()
        self.logger.debug("Using " + str(slate_date) + " to find slate")
        select_slate.add_where(FdSlates.date, slate_date)
        slate = self.db_manager.select_single(select_slate)
        self.logger.info("Using SLATE with ID " + str(slate.get(FdSlates.id)))
        select_games = database.entity(FdGames)
        select_games.add_where(FdGames.slate_id, slate.get(FdSlates.id))
        games = self.db_manager.select_all(select_games)
        self.logger.debug("Found " + str(len(games)) + " FD_GAMES for consideration")
        fd_players_stats = []
        for game in games:
            extend_list_select = database.entity(FdPlayerStats)
            extend_list_select.add_where(FdPlayerStats.game_id, game.get(FdGames.id))
            extend_list = self.db_manager.select_all(extend_list_select)
            fd_players_stats.extend(extend_list)
        self.logger.debug("Found " + str(len(fd_players_stats)) + " FD_PLAYER_STATS for consideration")
        fd_players_select = database.entity(FdPlayers)
        fd_players = self.db_manager.select_all(fd_players_select)
        insert_lp_input_list = []
        for fd_player_stats in fd_players_stats:
            for fd_player in fd_players:
                if fd_player_stats.get(FdPlayerStats.player_id) == fd_player.get(FdPlayers.id):
                    self.logger.debug("Using FD_PLAYER_STATS for PLAYER with FD_PLAYER ID " +
                                      str(fd_player.get(FdPlayers.id)))
                    if fd_player.get(FdPlayers.nhl_id) is not None:
                        self.logger.debug("Found NHL PLAYER with ID" +
                                          str(fd_player.get(FdPlayers.nhl_id)))
                        select_fd_game = database.entity(FdGames)
                        select_fd_game.add_where(FdGames.id, fd_player_stats.get(FdPlayerStats.game_id))
                        fd_game = self.db_manager.select_single(select_fd_game)
                        if fd_player_stats.get(FdPlayerStats.position) == 'G':
                            pred_stat_table = GoaliePredStats
                        else:
                            pred_stat_table = PlayerPredStats
                        select_pred_stats = database.entity(pred_stat_table)
                        select_pred_stats.add_where(pred_stat_table.game_id, fd_game.get(FdGames.nhl_game_id))
                        select_pred_stats.add_where(pred_stat_table.player_id, fd_player.get(FdPlayers.nhl_id))
                        pred_stats = self.db_manager.select_single(select_pred_stats)
                        if pred_stats is not None:
                            self.logger.debug("Found NHL PRED STATS for NHL PLAYER with ID " +
                                              str(fd_player.get(FdPlayers.nhl_id)) +
                                              " and FD GAME with ID " +
                                              str(fd_game.get(FdGames.id)))
                            insert_lp_input_item = database.entity(LpInputs)
                            insert_lp_input_item.set(LpInputs.slate_id, slate.get(FdSlates.id))
                            insert_lp_input_item.set(LpInputs.nhl_player_id, fd_player.get(FdPlayers.nhl_id))
                            insert_lp_input_item.set(LpInputs.nhl_game_id, pred_stats.get(pred_stat_table.game_id))
                            insert_lp_input_item.set(LpInputs.fd_position, fd_player_stats.get(FdPlayerStats.position))
                            insert_lp_input_item.set(LpInputs.pred_fd_score, pred_stats.get(pred_stat_table.fd_score))
                            insert_lp_input_item.set(LpInputs.fd_salary, fd_player_stats.get(FdPlayerStats.salary))
                            insert_lp_input_list.append(insert_lp_input_item)
                        else:
                            self.logger.info("No PRED STATS exist for NHL PLAYER with ID " +
                                             str(fd_player.get(FdPlayers.nhl_id)) +
                                             " and FD GAME with ID " +
                                             str(fd_game.get(FdGames.id)))

                    else:
                        self.logger.warning("Cannot insert FD_PLAYER_STATS with FD_PLAYER ID " +
                                            str(fd_player.get(FdPlayers.id)) +
                                            " into LP_INPUT because no matching NHL PLAYER exists.")
                    break
        self.db_manager.insert(insert_lp_input_list, commit=False)

    def calculate_lineup(self, predicted=True):
        self.logger.info("Attempting to calculate LP lineup that is " +
                         "" if predicted else "not " +
                         "predicted")
        select_slate = database.entity(FdSlates)
        slate_date = date.today()
        if not predicted:
            slate_date -= timedelta(days=1)
        self.logger.debug("Using " + str(slate_date) + " to find slate")
        select_slate.add_where(FdSlates.date, slate_date)
        slate = self.db_manager.select_single(select_slate)
        select_lp_inputs = database.entity(LpInputs)
        select_lp_inputs.add_where(LpInputs.slate_id, slate.get(FdSlates.id))
        lp_inputs = self.db_manager.select_all(select_lp_inputs)
        self.logger.debug("Found " +
                          str(len(lp_inputs)) +
                          " LP_INPUTS for consideration using SLATE with ID " +
                          str(slate.get(FdSlates.id)))
        problem_status, problem_variables = self.solve_lp_problem(lp_inputs, predicted)
        self.handle_lp_data(slate, problem_status, problem_variables, lp_inputs, predicted)

    def solve_lp_problem(self, lp_inputs, predicted):
        self.logger.info("Attempting to solve LP problem")
        selection_dict = {}
        for lp_input in lp_inputs:
            position = lp_input.get(LpInputs.fd_position)
            if position in selection_dict:
                selection_dict[position].append(lp_input)
            else:
                selection_dict[position] = [lp_input]
        position_count = {'C': 2,
                          'W': 4,
                          'D': 2,
                          'G': 1}
        lp_vars = {}
        for lp_input in lp_inputs:
            lp_vars[lp_input.get(LpInputs.nhl_player_id)] = LpVariable(str(lp_input.get(LpInputs.nhl_player_id)),
                                                                       cat="Binary")

        self.logger.debug("Solving with " + str(len(lp_inputs)) + " total variables")
        for key, val in selection_dict.items():
            self.logger.debug("Solving with " + str(len(val)) + " " + key)

        problem = LpProblem("Lineup_Solver", LpMaximize)
        problem += LpAffineExpression([(lp_vars[lp_input.get(LpInputs.nhl_player_id)],
                                        lp_input.get(LpInputs.fd_salary)) for lp_input in lp_inputs]) <= 55000
        problem += LpAffineExpression([(lp_vars[lp_input.get(LpInputs.nhl_player_id)],
                                        lp_input.get(LpInputs.pred_fd_score)
                                        if predicted else lp_input.get(LpInputs.act_fd_score))
                                       for lp_input in lp_inputs])
        for position, pos_lp_inputs in selection_dict.items():
            problem += LpAffineExpression([(lp_vars[pos_lp_input.get(LpInputs.nhl_player_id)], 1)
                                           for pos_lp_input in pos_lp_inputs]) == position_count[position]

        try:
            problem.solve()
        except PulpSolverError as e:
            self.logger.exception("Error solving LP problem with STATUS " +
                                  problem.status +
                                  " possibly due to duplicate variables?")
            raise e

        return problem.status, problem.variables()

    def handle_lp_data(self, slate, problem_status, problem_variables, lp_inputs, predicted):
        self.logger.info("Attempting to insert new LP data results to DB")
        insert_lp_players = []
        total_salary = 0
        total_points = 0.0
        email_content = ""
        for lp_variable in problem_variables:
            if lp_variable.varValue > 0:
                for lp_input in lp_inputs:
                    if int(lp_variable.name) == lp_input.get(LpInputs.nhl_player_id):
                        if predicted:
                            score = lp_input.get(LpInputs.pred_fd_score)
                        else:
                            score = lp_input.get(LpInputs.act_fd_score)
                        position = lp_input.get(LpInputs.fd_position)
                        salary = lp_input.get(LpInputs.fd_salary)
                        insert_lp_player = database.entity(LpLineupPlayers)
                        insert_lp_player.set(LpLineupPlayers.nhl_id, int(lp_variable.name))
                        insert_lp_player.set(LpLineupPlayers.position, position)
                        insert_lp_player.set(LpLineupPlayers.salary, salary)
                        insert_lp_player.set(LpLineupPlayers.fd_score, score)
                        insert_lp_players.append(insert_lp_player)
                        player_string = lp_variable.name
                        player_string += " POSITION: "
                        player_string += position
                        player_string += " SALARY: $"
                        player_string += str(salary)
                        player_string += " SCORE: "
                        player_string += str(score)
                        email_content += player_string + "\n"
                        self.logger.info(player_string)
                        total_salary += salary
                        total_points += score
                        break

        total_salary_string = "TOTAL SALARY: $" + str(total_salary)
        total_points_string = "TOTAL POINTS: " + str(total_points)
        email_content += "\n\n"
        email_content += total_salary_string + "\n\n"
        email_content += total_points_string
        self.logger.info(total_salary_string)
        self.logger.info(total_points_string)

        try:
            email_manager = EmailManager(Constants.LOGGING_EMAIL_HOST,
                                         Constants.LOGGING_EMAIL_USERNAME,
                                         Constants.LOGGING_EMAIL_PASSWORD,
                                         Constants.LOGGING_FROM_EMAIL)
            if predicted:
                subject = "TODAY PREDICTED LINEUP"
            else:
                subject = "YESTERDAY PERFECT LINEUP"
            email_manager.send_email(Constants.LOGGING_TO_EMAIL,
                                     subject,
                                     email_content)
        except TimeoutError:
            self.logger.error("Timeout error while sending LP result email")

        if predicted:
            self.logger.info("Deleting previous predicted lineup if it exists.")
            select_lp_lineup = database.entity(LpLineups)
            select_lp_lineup.add_where(LpLineups.slate_id, slate.get(FdSlates.id))
            select_lp_lineup.add_where(LpLineups.is_actual, False)
            select_lp_lineup.add_where(LpLineups.is_perfect, False)
            select_lp_lineup.add_where(LpLineups.user_modified, False)
            existing_lp_lineup = self.db_manager.select_single(select_lp_lineup)
            if existing_lp_lineup is not None:
                self.logger.debug("Found previous predicted lineup with ID " +
                                  str(existing_lp_lineup.get(LpLineups.id)) +
                                  " to be deleted.")
                select_lp_lineup_players = database.entity(LpLineupPlayers)
                select_lp_lineup_players.add_where(LpLineupPlayers.lineup_id, existing_lp_lineup.get(LpLineups.id))
                lp_lineup_players = self.db_manager.select_all(select_lp_lineup_players)
                if lp_lineup_players is not None:
                    self.logger.debug("Found " +
                                      str(len(lp_lineup_players)) +
                                      " previous lineup players to be deleted.")
                    self.db_manager.delete(lp_lineup_players, commit=False)
            self.db_manager.delete(existing_lp_lineup, commit=False)

        self.logger.debug("Inserting new lineup and lineup players")

        insert_lp_lineup = database.entity(LpLineups)
        insert_lp_lineup.set(LpLineups.slate_id, slate.get(FdSlates.id))
        insert_lp_lineup.set(LpLineups.is_actual, False)
        insert_lp_lineup.set(LpLineups.is_perfect, predicted)
        insert_lp_lineup.set(LpLineups.result, LpStatus[problem_status])
        insert_lp_lineup.set(LpLineups.total_salary, total_salary)
        insert_lp_lineup.set(LpLineups.total_points, total_points)
        insert_lp_lineup.set(LpLineups.date_time, datetime.now())
        lineup_id = self.db_manager.insert(insert_lp_lineup, commit=False)

        for insert_lp_player in insert_lp_players:
            insert_lp_player.set(LpLineupPlayers.lineup_id, lineup_id)

        self.db_manager.insert(insert_lp_players, commit=False)
