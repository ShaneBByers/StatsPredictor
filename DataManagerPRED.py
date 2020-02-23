import logging
from datetime import datetime
from database import database
from Generated.DatabaseClasses import *


class DataManagerPRED:

    def __init__(self, logger_name, db_manager):
        self.logger = logging.getLogger(logger_name)

        self.db_manager = db_manager

    def current_day_functions(self):
        self.get_pred_player_stats()

    def get_pred_player_stats(self):
        select_season = database.entity(Seasons)
        select_season.add_where(Seasons.is_current, True)
        season = self.db_manager.select_single(select_season)
        select_player_pred_stats = database.entity(PlayerPredStats)
        select_player_pred_stats.add_order_by(PlayerPredStats.game_id, False)
        last_player_pred_stats = self.db_manager.select_single(select_player_pred_stats)
        last_game_id = last_player_pred_stats.get(PlayerPredStats.game_id)
        select_last_completed_game = database.entity(Games)
        select_last_completed_game.add_where(Games.id, last_game_id)
        select_last_completed_game.add_where(Games.is_home, True)
        last_completed_game = self.db_manager.select_single(select_last_completed_game)
        start_date_time = last_completed_game.get(Games.date_time)
        start_date_time = start_date_time.combine(start_date_time.date(), datetime.max.time())
        end_date_time = datetime.today()
        end_date_time = end_date_time.combine(end_date_time.date(), datetime.min.time())
        select_games_to_complete = database.entity(Games)
        select_games_to_complete.add_where(Games.date_time, start_date_time, ">")
        select_games_to_complete.add_where(Games.date_time, end_date_time, "<")
        select_games_to_complete.add_where(Games.is_home, True)
        games_to_complete = self.db_manager.select_all(select_games_to_complete)
        for game_to_complete in games_to_complete:
            self.get_pred_player_stats_for_game(season, game_to_complete)

    def get_pred_player_stats_for_game(self, season, game_to_complete):
        select_fd_game = database.entity(FdGames)
        select_fd_game.add_where(FdGames.nhl_game_id, game_to_complete.get(Games.id))
        fd_game = self.db_manager.select_single(select_fd_game)
        nhl_players_dict = {}
        if fd_game is not None:
            select_fd_players_stats = database.entity(FdPlayerStats)
            select_fd_players_stats.add_where(FdPlayerStats.game_id, fd_game.get(FdGames.id))
            fd_players_stats = self.db_manager.select_all(select_fd_players_stats)
            for fd_player_stats in fd_players_stats:
                select_fd_team = database.entity(FdTeams)
                select_fd_team.add_where(FdTeams.id, fd_player_stats.get(FdPlayerStats.team_id))
                fd_team = self.db_manager.get(select_fd_team)
                nhl_team_id = fd_team.get(FdTeams.nhl_id)
                select_fd_player = database.entity(FdPlayers)
                select_fd_player.add_where(FdPlayers.id, fd_player_stats.get(FdPlayerStats.player_id))
                fd_player = self.db_manager.select_single(select_fd_player)
                nhl_player_id = fd_player.get(FdPlayers.nhl_id)
                if nhl_player_id is not None:
                    if fd_player_stats.get(FdPlayerStats.position) == 'G':
                        stats_table = GoalieStats
                    else:
                        stats_table = PlayerStats
                    nhl_players_dict[nhl_player_id] = {"TEAM_ID": nhl_team_id,
                                                       "STATS_TABLE": stats_table}
        else:
            select_nhl_players_stats = database.entity(PlayerStats)
            select_nhl_players_stats.add_where(PlayerStats.game_id, game_to_complete.get(Games.id))
            nhl_players_stats = self.db_manager.select_all(select_nhl_players_stats)
            for nhl_player_stats in nhl_players_stats:
                select_nhl_player = database.entity(Players)
                select_nhl_player.add_where(Players.id, nhl_player_stats.get(PlayerStats.player_id))
                nhl_player = self.db_manager.select_single(select_nhl_player)
                nhl_players_dict[nhl_player.get(Players.id)] = {"TEAM_ID": nhl_player_stats.get(PlayerStats.team_id),
                                                                "STATS_TABLE": PlayerStats}
            select_nhl_goalies_stats = database.entity(GoalieStats)
            select_nhl_goalies_stats.add_where(GoalieStats.game_id, game_to_complete.get(Games.id))
            nhl_goalies_stats = self.db_manager.select_all(select_nhl_goalies_stats)
            for nhl_goalie_stats in nhl_goalies_stats:
                select_nhl_goalie = database.entity(Players)
                select_nhl_goalie.add_where(Players.id, nhl_goalie_stats.get(GoalieStats.player_id))
                nhl_goalie = self.db_manager.select_single(select_nhl_goalie)
                nhl_players_dict[nhl_goalie.get(Players.id)] = {"TEAM_ID": nhl_goalie_stats.get(PlayerStats.team_id),
                                                                "STATS_TABLE": GoalieStats}
        select_first_game = database.entity(Games)
        select_first_game.add_where(Games.is_home, True)
        select_first_game.add_where(Games.season_id, season.get(Seasons.id))
        select_first_game.add_order_by(Games.id)
        first_game = self.db_manager.select_single(select_first_game)
        for nhl_player_id, info_dict in nhl_players_dict.items():
            stats_table = info_dict["STATS_TABLE"]
            select_player_goalie_stats = database.entity(stats_table)
            select_player_goalie_stats.add_where(stats_table.player_id, nhl_player_id)
            select_player_goalie_stats.add_where(stats_table.game_id, first_game.get(Games.id), ">=")
            player_goalie_stats = self.db_manager.select_all(select_player_goalie_stats)
            if stats_table == GoalieStats:
                self.insert_goalie_stats(goalie_stats_list=player_goalie_stats,
                                         nhl_game_id=game_to_complete.get(Games.id),
                                         nhl_team_id=info_dict["TEAM_ID"],
                                         nhl_player_id=nhl_player_id)
            else:
                self.insert_player_stats(player_stats_list=player_goalie_stats,
                                         nhl_game_id=game_to_complete.get(Games.id),
                                         nhl_team_id=info_dict["TEAM_ID"],
                                         nhl_player_id=nhl_player_id)

    def insert_goalie_stats(self, goalie_stats_list, nhl_game_id, nhl_team_id, nhl_player_id):
        saves = 0.0
        ga = 0.0
        is_win = 0.0
        is_shutout = 0.0
        for game_goalie_stats in goalie_stats_list:
            total_shots = game_goalie_stats.get(GoalieStats.total_shots)
            total_saves = game_goalie_stats.get(GoalieStats.total_saves)
            saves += total_saves
            game_ga = total_shots - total_saves
            ga += game_ga
            is_win += game_goalie_stats.get(GoalieStats.decision) == 'W'
            is_shutout += total_shots == total_saves
        count = len(goalie_stats_list)
        if count > 0:
            saves /= count
            ga /= count
            is_win /= count
            is_shutout /= count
        insert_goalie_pred_stats = database.entity(GoaliePredStats)
        insert_goalie_pred_stats.set(GoaliePredStats.game_id, nhl_game_id)
        insert_goalie_pred_stats.set(GoaliePredStats.team_id, nhl_team_id)
        insert_goalie_pred_stats.set(GoaliePredStats.player_id, nhl_player_id)
        insert_goalie_pred_stats.set(GoaliePredStats.saves, saves)
        insert_goalie_pred_stats.set(GoaliePredStats.ga, ga)
        insert_goalie_pred_stats.set(GoaliePredStats.is_win, is_win)
        insert_goalie_pred_stats.set(GoaliePredStats.is_shutout, is_shutout)
        fd_score = 0.0
        fd_score += is_win * 12
        fd_score += is_shutout * 8
        fd_score += saves * 0.8
        fd_score -= ga * 4
        insert_goalie_pred_stats.set(GoaliePredStats.fd_score, fd_score)
        self.db_manager.insert(insert_goalie_pred_stats)

    def insert_player_stats(self, player_stats_list, nhl_game_id, nhl_team_id, nhl_player_id):
        goals = 0.0
        assists = 0.0
        ppg = 0.0
        ppa = 0.0
        shg = 0.0
        sha = 0.0
        shots = 0.0
        blocked = 0.0
        for game_player_stats in player_stats_list:
            goals += game_player_stats.get(PlayerStats.goals)
            assists += game_player_stats.get(PlayerStats.assists)
            ppg += game_player_stats.get(PlayerStats.ppg)
            ppa += game_player_stats.get(PlayerStats.ppa)
            shg += game_player_stats.get(PlayerStats.shg)
            sha += game_player_stats.get(PlayerStats.sha)
            shots += game_player_stats.get(PlayerStats.shots)
            blocked += game_player_stats.get(PlayerStats.blocked)
        count = len(player_stats_list)
        if count > 0:
            goals /= count
            assists /= count
            ppg /= count
            ppa /= count
            shg /= count
            sha /= count
            shots /= count
            blocked /= count
        insert_player_pred_stats = database.entity(PlayerPredStats)
        insert_player_pred_stats.set(PlayerPredStats.game_id, nhl_game_id)
        insert_player_pred_stats.set(PlayerPredStats.team_id, nhl_team_id)
        insert_player_pred_stats.set(PlayerPredStats.player_id, nhl_player_id)
        insert_player_pred_stats.set(PlayerPredStats.goals, goals)
        insert_player_pred_stats.set(PlayerPredStats.assists, assists)
        insert_player_pred_stats.set(PlayerPredStats.shots, shots)
        insert_player_pred_stats.set(PlayerPredStats.ppg, ppg)
        insert_player_pred_stats.set(PlayerPredStats.ppa, ppa)
        insert_player_pred_stats.set(PlayerPredStats.shg, shg)
        insert_player_pred_stats.set(PlayerPredStats.sha, sha)
        insert_player_pred_stats.set(PlayerPredStats.blocked, blocked)
        fd_score = 0.0
        fd_score += goals * 12
        fd_score += assists * 8
        fd_score += ppg * 0.5
        fd_score += ppa * 0.5
        fd_score += shg * 2
        fd_score += sha * 2
        fd_score += shots * 1.6
        fd_score += blocked * 1.6
        insert_player_pred_stats.set(PlayerPredStats.fd_score, fd_score)
        self.db_manager.insert(insert_player_pred_stats)