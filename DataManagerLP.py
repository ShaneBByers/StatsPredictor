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
            self.logger.info("Getting yesterday's perfect lineup")
            self.calculate_lineup(actual=True)
            self.db_manager.commit()
            self.logger.info("Setting up LP input data")
            self.setup_lp_input()
            self.logger.info("Getting today's predicted lineup")
            self.calculate_lineup(actual=False)
            self.db_manager.commit()
        except Exception as e:
            self.logger.exception("ERROR IN LP CURRENT DAY")
            raise e

    def calculate_lineup(self, actual=False):
        select_slate = database.entity(FdSlates)
        slate_date = date.today()
        if actual:
            slate_date -= timedelta(days=1)
        self.logger.debug("Using " + str(slate_date) + " to find slate")
        select_slate.add_where(FdSlates.date, slate_date)
        slate = self.db_manager.select_single(select_slate)
        if actual:
            select_actual_lp_lineup = database.entity(LpLineup)
            select_actual_lp_lineup.add_where(LpLineup.slate_id, slate.get(FdSlates.id))
            select_actual_lp_lineup.add_where(LpLineup.is_actual, True)
            actual_lp_lineup = self.db_manager.select_single(select_actual_lp_lineup)
            if actual_lp_lineup is not None:
                self.logger.info("Actual LP LINEUP already exists for SLATE with ID " +
                                 str(slate.get(FdSlates.id)))
                return
        self.logger.info("Using SLATE with ID " + str(slate.get(FdSlates.id)))
        select_games = database.entity(FdGames)
        select_games.add_where(FdGames.slate_id, slate.get(FdSlates.id))
        games = self.db_manager.select_all(select_games)
        self.logger.debug("Found " + str(len(games)) + " FD_GAMES for consideration")
        fd_player_stats = []
        for game in games:
            extend_list_select = database.entity(FdPlayerStats)
            extend_list_select.add_where(FdPlayerStats.game_id, game.get(FdGames.id))
            extend_list = self.db_manager.select_all(extend_list_select)
            fd_player_stats.extend(extend_list)
        self.logger.debug("Found " + str(len(fd_player_stats)) + " FD_PLAYER_STATS for consideration")
        selection_dict, player_details_dict = self.get_dicts_from_player_stats(fd_player_stats, actual)
        problem_status, problem_variables = self.solve_lp_problem(selection_dict)
        self.handle_lp_data(slate, problem_status, problem_variables, player_details_dict, actual)

    def get_dicts_from_player_stats(self, fd_player_stats, actual):
        self.logger.debug("Attempting to get selection and pred score dictionaries for all player stats.")
        selection_dict = {'C': [],
                          'W': [],
                          'D': [],
                          'G': []}
        player_details_dict = {}
        for fd_player_stat in fd_player_stats:
            select_fd_player = database.entity(FdPlayers)
            select_fd_player.add_where(FdPlayers.id, fd_player_stat.get(FdPlayerStats.player_id))
            fd_player = self.db_manager.select_single(select_fd_player)
            select_fd_game = database.entity(FdGames)
            select_fd_game.add_where(FdGames.id, fd_player_stat.get(FdPlayerStats.game_id))
            fd_game = self.db_manager.select_single(select_fd_game)
            score = None
            if actual:
                if fd_player_stat.get(FdPlayerStats.position) == 'G':
                    score = self.get_actual_goalie_fd_score(fd_game.get(FdGames.nhl_game_id),
                                                            fd_player.get(FdPlayers.nhl_id))
                else:
                    score = self.get_actual_player_fd_score(fd_game.get(FdGames.nhl_game_id),
                                                            fd_player.get(FdPlayers.nhl_id))
            else:
                if fd_player_stat.get(FdPlayerStats.position) == 'G':
                    pred_stat_table = GoaliePredStats
                else:
                    pred_stat_table = PlayerPredStats
                select_player_pred_stats = database.entity(pred_stat_table)
                select_player_pred_stats.add_where(pred_stat_table.player_id, fd_player.get(FdPlayers.nhl_id))
                select_player_pred_stats.add_where(pred_stat_table.game_id, fd_game.get(FdGames.nhl_game_id))
                player_goalie_pred_stat = self.db_manager.select_single(select_player_pred_stats)
                if player_goalie_pred_stat is not None:
                    score = player_goalie_pred_stat.get(pred_stat_table.fd_score)
            if score is not None:
                inner_dict = {"NHL_PLAYER_ID": fd_player.get(FdPlayers.nhl_id),
                              "SCORE": score,
                              "SALARY": fd_player_stat.get(FdPlayerStats.salary),
                              "LP_VARIABLE": LpVariable(str(fd_player.get(FdPlayers.nhl_id)),  cat="Binary")}
                position = fd_player_stat.get(FdPlayerStats.position)
                nhl_id = fd_player.get(FdPlayers.nhl_id)
                if inner_dict not in selection_dict[position]:
                    self.logger.debug("Creating dictionaries for NHL_PLAYER with ID " + str(nhl_id))
                    player_details_dict[nhl_id] = {"SCORE": score,
                                                   "FD_GAME_ID": fd_player_stat.get(FdPlayerStats.game_id)}
                    selection_dict[position].append(inner_dict)
                else:
                    self.logger.warning("NHL_PLAYER with ID " +
                                        str(nhl_id) +
                                        " exists on multiple teams. Prediction could be wrong.")
        return selection_dict, player_details_dict

    def solve_lp_problem(self, selection_dict):
        self.logger.info("Attempting to solve LP problem")
        all_vars = selection_dict['C'].copy()
        all_vars.extend(selection_dict['W'])
        all_vars.extend(selection_dict['D'])
        all_vars.extend(selection_dict['G'])

        self.logger.debug("Solving with " + str(len(all_vars)) + " total variables")
        self.logger.debug("Solving with " + str(len(selection_dict['C'])) + " Centers")
        self.logger.debug("Solving with " + str(len(selection_dict['W'])) + " Wingers")
        self.logger.debug("Solving with " + str(len(selection_dict['D'])) + " Defense")
        self.logger.debug("Solving with " + str(len(selection_dict['G'])) + " Goalies")

        problem = LpProblem("Lineup_Solver", LpMaximize)
        problem += LpAffineExpression([(var["LP_VARIABLE"], var["SCORE"]) for var in all_vars])
        problem += LpAffineExpression([(var["LP_VARIABLE"], 1) for var in selection_dict['C']]) == 2
        problem += LpAffineExpression([(var["LP_VARIABLE"], 1) for var in selection_dict['W']]) == 4
        problem += LpAffineExpression([(var["LP_VARIABLE"], 1) for var in selection_dict['D']]) == 2
        problem += LpAffineExpression([(var["LP_VARIABLE"], 1) for var in selection_dict['G']]) == 1
        problem += LpAffineExpression([(var["LP_VARIABLE"], var["SALARY"]) for var in all_vars]) <= 55000

        try:
            problem.solve()
        except PulpSolverError as e:
            self.logger.exception("Error solving LP problem with STATUS " +
                                  problem.status +
                                  " possibly due to duplicate variables?")
            raise e

        return problem.status, problem.variables()

    def handle_lp_data(self, slate, problem_status, problem_variables, player_details_dict, actual):
        self.logger.info("Attempting to insert new LP data results to DB")
        insert_lp_players = []
        total_salary = 0
        total_points = 0.0
        email_content = ""
        for lp_variable in problem_variables:
            if lp_variable.varValue > 0:
                select_fd_player = database.entity(FdPlayers)
                select_fd_player.add_where(FdPlayers.nhl_id, int(lp_variable.name))
                fd_player = self.db_manager.select_single(select_fd_player)
                select_fd_player_stats = database.entity(FdPlayerStats)
                select_fd_player_stats.add_where(FdPlayerStats.player_id, fd_player.get(FdPlayers.id))
                select_fd_player_stats.add_where(FdPlayerStats.game_id,
                                                 player_details_dict[int(lp_variable.name)]["FD_GAME_ID"])
                fd_player_stats = self.db_manager.select_single(select_fd_player_stats)
                score = player_details_dict[int(lp_variable.name)]["SCORE"]
                insert_lp_player = database.entity(LpPlayers)
                insert_lp_player.set(LpPlayers.nhl_id, int(lp_variable.name))
                insert_lp_player.set(LpPlayers.position, fd_player_stats.get(FdPlayerStats.position))
                insert_lp_player.set(LpPlayers.salary, fd_player_stats.get(FdPlayerStats.salary))
                insert_lp_player.set(LpPlayers.fd_score, score)
                insert_lp_players.append(insert_lp_player)
                player_string = str(fd_player.get(FdPlayers.full_name))
                player_string += " POSITION: "
                player_string += fd_player_stats.get(FdPlayerStats.position)
                player_string += " SALARY: $"
                player_string += str(fd_player_stats.get(FdPlayerStats.salary))
                player_string += " SCORE: "
                player_string += str(score)
                email_content += player_string + "\n"
                self.logger.info(player_string)
                total_salary += fd_player_stats.get(FdPlayerStats.salary)
                total_points += score

        total_salary_string = "TOTAL SALARY: $" + str(total_salary)
        total_points_string = "TOTAL POINTS: " + str(total_points)
        email_content += "\n\n"
        email_content += total_salary_string + "\n\n"
        email_content += total_points_string
        if actual:
            self.logger.debug("Getting max predicted points from yesterday for SLATE with ID" +
                              str(slate.get(FdSlates.id)))
            yesterday_pred_points_select = database.entity(LpLineup)
            yesterday_pred_points_select.add_where(LpLineup.slate_id, slate.get(FdSlates.id))
            yesterday_pred_points_select.add_where(LpLineup.is_actual, False)
            yesterday_pred_points_select.add_order_by(LpLineup.total_points, False)
            yesterday_pred_points = self.db_manager.select_single(yesterday_pred_points_select)
            yesterday_points = yesterday_pred_points.get(LpLineup.total_points)
            yesterday_pred_points_string = "YESTERDAY PREDICTED POINTS: " + str(yesterday_points)
            email_content += "\n\n" + yesterday_pred_points_string
        self.logger.info(total_salary_string)
        self.logger.info(total_points_string)

        try:
            email_manager = EmailManager(Constants.LOGGING_EMAIL_HOST,
                                         Constants.LOGGING_EMAIL_USERNAME,
                                         Constants.LOGGING_EMAIL_PASSWORD,
                                         Constants.LOGGING_FROM_EMAIL)
            if actual:
                subject = "YESTERDAY PERFECT LINEUP"
            else:
                subject = "TODAY PREDICTED LINEUP"
            email_manager.send_email(Constants.LOGGING_TO_EMAIL,
                                     subject,
                                     email_content)
        except TimeoutError:
            self.logger.error("Timeout error while sending LP result email")

        insert_lp_lineup = database.entity(LpLineup)
        insert_lp_lineup.set(LpLineup.slate_id, slate.get(FdSlates.id))
        insert_lp_lineup.set(LpLineup.is_actual, actual)
        insert_lp_lineup.set(LpLineup.result, LpStatus[problem_status])
        insert_lp_lineup.set(LpLineup.total_salary, total_salary)
        insert_lp_lineup.set(LpLineup.total_points, total_points)
        insert_lp_lineup.set(LpLineup.date_time, datetime.now())
        lineup_id = self.db_manager.insert(insert_lp_lineup, commit=False)

        for insert_lp_player in insert_lp_players:
            insert_lp_player.set(LpPlayers.lineup_id, lineup_id)

        self.db_manager.insert(insert_lp_players, commit=False)

    def get_actual_player_fd_score(self, nhl_game_id, nhl_player_id):
        self.logger.debug("Getting player stats for PLAYER with ID " +
                          str(nhl_player_id) +
                          " and GAME with ID " +
                          str(nhl_game_id))
        select_player_stats = database.entity(PlayerStats)
        select_player_stats.add_where(PlayerStats.game_id, nhl_game_id)
        select_player_stats.add_where(PlayerStats.player_id, nhl_player_id)
        player_stats = self.db_manager.select_single(select_player_stats)
        if player_stats is not None:
            score = 0.0
            score += player_stats.get(PlayerStats.goals) * 12
            score += player_stats.get(PlayerStats.assists) * 8
            score += player_stats.get(PlayerStats.ppg) * 0.5
            score += player_stats.get(PlayerStats.ppa) * 0.5
            score += player_stats.get(PlayerStats.shg) * 2
            score += player_stats.get(PlayerStats.sha) * 2
            score += player_stats.get(PlayerStats.shots) * 1.6
            score += player_stats.get(PlayerStats.blocked) * 1.6
            self.logger.debug("Found player with FD SCORE of " + str(score))
            return score
        else:
            self.logger.info("Could not find yesterday's PLAYER STATS for GAME with ID " +
                             str(nhl_game_id) +
                             " and PLAYER with ID " +
                             str(nhl_player_id))
            return None

    def get_actual_goalie_fd_score(self, nhl_game_id, nhl_goalie_id):
        self.logger.debug("Getting goalie stats for GOALIE with ID " +
                          str(nhl_goalie_id) +
                          " and GAME with ID " +
                          str(nhl_game_id))
        select_goalie_stats = database.entity(GoalieStats)
        select_goalie_stats.add_where(GoalieStats.game_id, nhl_game_id)
        select_goalie_stats.add_where(GoalieStats.player_id, nhl_goalie_id)
        goalie_stats = self.db_manager.select_single(select_goalie_stats)
        if goalie_stats is not None:
            score = 0.0
            is_win = goalie_stats.get(GoalieStats.decision) == 'W'
            total_shots = goalie_stats.get(GoalieStats.total_shots)
            total_saves = goalie_stats.get(GoalieStats.total_saves)
            is_shutout = total_shots == total_saves
            ga = total_shots - total_saves
            score += is_win * 12
            score += is_shutout * 8
            score += total_saves * 0.8
            score -= ga * 4
            self.logger.debug("Found goalie with FD SCORE of " + str(score))
            return score
        else:
            self.logger.warning("Could not find yesterday's GOALIE STATS for GAME with ID " +
                                str(nhl_game_id) +
                                " and GOALIE with ID " +
                                str(nhl_goalie_id))
            return None
