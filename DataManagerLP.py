import logging
import Constants
from database import database
from pulp import LpProblem, LpAffineExpression, LpVariable, LpStatus, LpMaximize
from Generated.DatabaseClasses import *


class DataManagerLP:

    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)

        self.db_manager = database.connect(logger_name,
                                           Constants.DB_HOST,
                                           Constants.DB_USERNAME,
                                           Constants.DB_PASSWORD,
                                           Constants.DB_NAME)

    def calc_lineup(self):
        select_fd_player_stats = database.entity(FdPlayerStats)
        fd_player_stats = self.db_manager.select_all(select_fd_player_stats)
        selection_dict = {}
        for fd_player_stat in fd_player_stats:
            select_fd_player = database.entity(FdPlayers)
            select_fd_player.add_where(FdPlayers.id, fd_player_stat.get(FdPlayerStats.player_id))
            fd_player = self.db_manager.select_single(select_fd_player)
            if fd_player_stat.get(FdPlayerStats.salary) not in selection_dict:
                selection_dict[fd_player_stat.get(FdPlayerStats.salary)] = {}
            salary_dict = selection_dict[fd_player_stat.get(FdPlayerStats.salary)]
            select_player_pred_stats = database.entity(PlayerPredStats)
            select_player_pred_stats.add_where(PlayerPredStats.player_id, fd_player.get(FdPlayers.nhl_id))
            player_pred_stat = self.db_manager.select_single(select_player_pred_stats)
            if player_pred_stat is not None:
                inner_dict = {"NHL_PLAYER_ID": fd_player.get(FdPlayers.nhl_id),
                              "PRED_SCORE": player_pred_stat.get(PlayerPredStats.fd_score)}
                if fd_player_stat.get(FdPlayerStats.position) not in salary_dict:
                    salary_dict[fd_player_stat.get(FdPlayerStats.position)] = inner_dict
                elif inner_dict["PRED_SCORE"] > salary_dict[fd_player_stat.get(FdPlayerStats.position)]["PRED_SCORE"]:
                    salary_dict[fd_player_stat.get(FdPlayerStats.position)] = inner_dict
        center_vars = []
        wing_vars = []
        defense_vars = []
        for salary, salary_dict in selection_dict.items():
            for position, player_dict in salary_dict.items():
                append_dict = {"NHL_PLAYER_ID": player_dict["NHL_PLAYER_ID"],
                               "SALARY": salary,
                               "PRED_SCORE": player_dict["PRED_SCORE"],
                               "LP_VARIABLE": LpVariable(str(player_dict["NHL_PLAYER_ID"]), cat="Binary")}
                if position == "C":
                    center_vars.append(append_dict)
                elif position == "W":
                    wing_vars.append(append_dict)
                elif position == "D":
                    defense_vars.append(append_dict)

        all_vars = center_vars.copy()
        all_vars.extend(wing_vars)
        all_vars.extend(defense_vars)

        problem = LpProblem("Lineup_Solver", LpMaximize)
        problem += LpAffineExpression([(var["LP_VARIABLE"], var["PRED_SCORE"]) for var in all_vars])

        problem += LpAffineExpression([(var["LP_VARIABLE"], 1) for var in center_vars]) == 2
        problem += LpAffineExpression([(var["LP_VARIABLE"], 1) for var in wing_vars]) == 4
        problem += LpAffineExpression([(var["LP_VARIABLE"], 1) for var in defense_vars]) == 2

        problem += LpAffineExpression([(var["LP_VARIABLE"], var["SALARY"]) for var in all_vars]) <= 48000

        print(problem)

        problem.solve()

        print("Status: " + LpStatus[problem.status])

        total_salary = 0

        for v in problem.variables():
            if v.varValue > 0:
                select_nhl_player = database.entity(Players)
                select_nhl_player.add_where(Players.id, int(v.name))
                nhl_player = self.db_manager.select_single(select_nhl_player)
                name = nhl_player.get(Players.full_name)
                select_fd_player = database.entity(FdPlayers)
                select_fd_player.add_where(FdPlayers.nhl_id, int(v.name))
                fd_player = self.db_manager.select_single(select_fd_player)
                select_fd_player_stats = database.entity(FdPlayerStats)
                select_fd_player_stats.add_where(FdPlayerStats.player_id, fd_player.get(FdPlayers.id))
                fd_player_stats = self.db_manager.select_single(select_fd_player_stats)
                print(fd_player_stats.get(FdPlayerStats.position) + ": " + name + ": $" + str(fd_player_stats.get(FdPlayerStats.salary)))
                total_salary += fd_player_stats.get(FdPlayerStats.salary)

        print("Total salary: " + str(total_salary))