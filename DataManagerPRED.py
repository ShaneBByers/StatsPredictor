import logging
import Constants
from datetime import date
from database import database
from Generated.DatabaseClasses import *


class DataManagerPRED:

    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)

        self.db_manager = database.connect(logger_name,
                                           Constants.DB_HOST,
                                           Constants.DB_USERNAME,
                                           Constants.DB_PASSWORD,
                                           Constants.DB_NAME)

    def get_pred_player_stats(self):
        select_season = database.entity(Seasons)
        select_season.add_where(Seasons.is_current, True)
        season = self.db_manager.select_single(select_season)
        start_game_id = int(str(season.get(Seasons.id))[:4]) * 1000000
        select_slate = database.entity(FdSlates)
        select_slate.add_where(FdSlates.date, date.today())
        slate = self.db_manager.select_single(select_slate)
        select_games = database.entity(FdGames)
        select_games.add_where(FdGames.slate_id, slate.get(FdSlates.id))
        games = self.db_manager.select_all(select_games)
        for game in games:
            select_fd_players_stats = database.entity(FdPlayerStats)
            select_fd_players_stats.add_where(FdPlayerStats.game_id, game.get(FdGames.id))
            fd_players_stats = self.db_manager.select_all(select_fd_players_stats)
            for fd_player_stats in fd_players_stats:
                select_fd_team = database.entity(FdTeams)
                select_fd_team.add_where(FdTeams.id, fd_player_stats.get(FdPlayerStats.team_id))
                fd_team = self.db_manager.select_single(select_fd_team)
                select_fd_player = database.entity(FdPlayers)
                select_fd_player.add_where(FdPlayers.id, fd_player_stats.get(FdPlayerStats.player_id))
                fd_player = self.db_manager.select_single(select_fd_player)
                if fd_player.get(FdPlayers.nhl_id) is not None:
                    select_season_player_stats = database.entity(PlayerStats)
                    select_season_player_stats.add_where(PlayerStats.game_id, start_game_id, ">")
                    select_season_player_stats.add_where(PlayerStats.player_id, fd_player.get(FdPlayers.nhl_id))
                    season_player_stats = self.db_manager.select_all(select_season_player_stats)
                    goals = 0
                    assists = 0
                    ppg = 0
                    ppa = 0
                    shg = 0
                    sha = 0
                    shots = 0
                    blocked = 0
                    for game_player_stats in season_player_stats:
                        goals += game_player_stats.get(PlayerStats.goals)
                        assists += game_player_stats.get(PlayerStats.assists)
                        ppg += game_player_stats.get(PlayerStats.ppg)
                        ppa += game_player_stats.get(PlayerStats.ppa)
                        shg += game_player_stats.get(PlayerStats.shg)
                        sha += game_player_stats.get(PlayerStats.sha)
                        shots += game_player_stats.get(PlayerStats.shots)
                        blocked += game_player_stats.get(PlayerStats.blocked)
                    count = len(season_player_stats)
                    goals /= count
                    assists /= count
                    ppg /= count
                    ppa /= count
                    shg /= count
                    sha /= count
                    shots /= count
                    blocked /= count
                    insert_player_pred_stats = database.entity(PlayerPredStats)
                    insert_player_pred_stats.set(PlayerPredStats.game_id, game.get(FdGames.nhl_game_id))
                    insert_player_pred_stats.set(PlayerPredStats.team_id, fd_team.get(FdTeams.nhl_id))
                    insert_player_pred_stats.set(PlayerPredStats.player_id, fd_player.get(FdPlayers.nhl_id))
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
