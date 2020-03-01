import logging
from datetime import date, datetime
from database import database
from pulp import LpProblem, LpAffineExpression, LpVariable, LpStatus, LpMaximize, PulpSolverError
from Generated.DatabaseClasses import *


class DataManagerLP:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)

        self.db_manager = db_manager

    def current_day_functions(self):
        self.logger.info("RUNNING CURRENT DAY FUNCTIONS FOR LP")
        self.calculate_lineup()
        self.db_manager.commit()

    def calculate_lineup(self):
        select_slate = database.entity(FdSlates)
        select_slate.add_where(FdSlates.date, date.today())
        slate = self.db_manager.select_single(select_slate)
        self.logger.info("Using SLATE with ID " + slate.get(FdSlates.id))
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
        self.logger.debug("Found " + str(len(fd_player_stats)) + "FD_PLAYER_STATS for consideration")
        selection_dict, pred_score_dict = self.get_dicts_from_player_stats(fd_player_stats)
        problem_status, problem_variables = self.solve_lp_problem(selection_dict)
        self.insert_lp_data(slate, problem_status, problem_variables, pred_score_dict)

    def get_dicts_from_player_stats(self, fd_player_stats):
        self.logger.debug("Attempting to get selection and pred score dictionaries for all player stats.")
        selection_dict = {'C': [],
                          'W': [],
                          'D': [],
                          'G': []}
        pred_score_dict = {}
        for fd_player_stat in fd_player_stats:
            select_fd_player = database.entity(FdPlayers)
            select_fd_player.add_where(FdPlayers.id, fd_player_stat.get(FdPlayerStats.player_id))
            fd_player = self.db_manager.select_single(select_fd_player)
            if fd_player_stat.get(FdPlayerStats.position) == 'G':
                pred_stat_table = GoaliePredStats
            else:
                pred_stat_table = PlayerPredStats
            select_player_pred_stats = database.entity(pred_stat_table)
            select_player_pred_stats.add_where(pred_stat_table.player_id, fd_player.get(FdPlayers.nhl_id))
            player_goalie_pred_stat = self.db_manager.select_single(select_player_pred_stats)
            if player_goalie_pred_stat is not None:
                inner_dict = {"NHL_PLAYER_ID": fd_player.get(FdPlayers.nhl_id),
                              "PRED_SCORE": player_goalie_pred_stat.get(pred_stat_table.fd_score),
                              "SALARY": fd_player_stat.get(FdPlayerStats.salary),
                              "LP_VARIABLE": LpVariable(str(fd_player.get(FdPlayers.nhl_id)),  cat="Binary")}
                position = fd_player_stat.get(FdPlayerStats.position)
                nhl_id = fd_player.get(FdPlayers.nhl_id)
                if inner_dict not in selection_dict[position]:
                    self.logger.debug("Creating dictionaries for NHL_PLAYER with ID " + str(nhl_id))
                    pred_score_dict[nhl_id] = player_goalie_pred_stat.get(pred_stat_table.fd_score)
                    selection_dict[position].append(inner_dict)
                else:
                    self.logger.warning("NHL_PLAYER with ID " +
                                        str(nhl_id) +
                                        " exists on multiple teams. Prediction could be wrong.")
        return selection_dict, pred_score_dict

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
        problem += LpAffineExpression([(var["LP_VARIABLE"], var["PRED_SCORE"]) for var in all_vars])
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

    def insert_lp_data(self, slate, problem_status, problem_variables, pred_score_dict):
        self.logger.info("Attempting to insert new LP data results to DB")
        insert_lp_players = []
        total_salary = 0
        total_points = 0.0
        for lp_variable in problem_variables:
            if lp_variable.varValue > 0:
                select_fd_player = database.entity(FdPlayers)
                select_fd_player.add_where(FdPlayers.nhl_id, int(lp_variable.name))
                fd_player = self.db_manager.select_single(select_fd_player)
                select_fd_player_stats = database.entity(FdPlayerStats)
                select_fd_player_stats.add_where(FdPlayerStats.player_id, fd_player.get(FdPlayers.id))
                fd_player_stats = self.db_manager.select_single(select_fd_player_stats)
                insert_lp_player = database.entity(LpPlayers)
                insert_lp_player.set(LpPlayers.nhl_id, int(lp_variable.name))
                insert_lp_player.set(LpPlayers.position, fd_player_stats.get(FdPlayerStats.position))
                insert_lp_player.set(LpPlayers.salary, fd_player_stats.get(FdPlayerStats.salary))
                insert_lp_player.set(LpPlayers.fd_score, pred_score_dict[int(lp_variable.name)])
                insert_lp_players.append(insert_lp_player)
                self.logger.info(str(fd_player.get(FdPlayers.full_name)) +
                                  " POSITION: " +
                                  fd_player_stats.get(FdPlayerStats.position) +
                                  " SALARY: $" +
                                  str(fd_player_stats.get(FdPlayerStats.salary)) +
                                  " SCORE: " +
                                  str(pred_score_dict[int(lp_variable.name)]))
                total_salary += fd_player_stats.get(FdPlayerStats.salary)
                total_points += pred_score_dict[int(lp_variable.name)]

        self.logger.info("TOTAL SALARY: $" + str(total_salary))
        self.logger.info("TOTAL POINTS: " + str(total_points))

        insert_lp_lineup = database.entity(LpLineup)
        insert_lp_lineup.set(LpLineup.slate_id, slate.get(FdSlates.id))
        insert_lp_lineup.set(LpLineup.is_actual, False)
        insert_lp_lineup.set(LpLineup.result, LpStatus[problem_status])
        insert_lp_lineup.set(LpLineup.total_salary, total_salary)
        insert_lp_lineup.set(LpLineup.total_points, total_points)
        insert_lp_lineup.set(LpLineup.date_time, datetime.now())
        lineup_id = self.db_manager.insert(insert_lp_lineup, commit=False)

        for insert_lp_player in insert_lp_players:
            insert_lp_player.set(LpPlayers.lineup_id, lineup_id)

        self.db_manager.insert(insert_lp_players, commit=False)
