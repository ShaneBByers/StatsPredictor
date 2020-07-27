import logging
from database import database
from Generated.DatabaseClasses import *


class NetworkInputsHelpers:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.current_season_year = None
        self.player_stats_dict = {}
        self.player_stats_dict_year = None
        self.goalie_stats_dict = {}
        self.goalie_game_stats_dict = {}
        self.team_stats_dict = {}
        self.player_dict = {}
        self.team_division_dict = {}
        self.team_conference_dict = {}
        self.player_game_dict = {}
        self.team_game_dict = {}
        self.games_teams_dict = {}
        self.game_times_dict = {}

        self.method_list = []

    def get_avg_player_stat_from_season(self, player_stats, specific_stat, total=False):
        player_id = player_stats.get(PlayerStats.player_id)
        if player_id in self.player_stats_dict:
            total_stat = 0.0
            for single_player_stats in self.player_stats_dict[player_id]:
                single_amt = single_player_stats.get(specific_stat)
                if single_amt is None:
                    single_amt = 0.0
                total_stat += single_amt
            total_len = len(self.player_stats_dict[player_id])
            if total_len > 0:
                if total:
                    return total_stat
                else:
                    return total_stat / total_len
        return 0.0

    def get_opp_goalie_avg_stat_this_season(self, player_stats, specific_stat, divide_specific_stat=None):
        goalie_id = self.get_opp_goalie_id_with_most_toi(player_stats)
        if goalie_id in self.goalie_stats_dict:
            total_stat = 0.0
            total_len = 0
            for single_goalie_stats in self.goalie_stats_dict:
                if single_goalie_stats.get(GoalieStats.game_id) != player_stats.get(PlayerStats.game_id):
                    single_amt = single_goalie_stats.get(specific_stat)
                    if single_amt is None:
                        single_amt = 0.0
                    else:
                        if divide_specific_stat is not None:
                            divide_amt = single_goalie_stats.get(divide_specific_stat)
                            if divide_amt is not None and divide_amt != 0.0:
                                single_amt /= divide_amt
                    total_stat += single_amt
                    total_len += 1
            if total_len > 0:
                return total_stat / total_len
        return 0.0

    def get_avg_team_stat_from_season(self, player_stats, specific_stat, opponent=False):
        team_id = player_stats.get(PlayerStats.team_id)
        if opponent:
            game_id = player_stats.get(PlayerStats.game_id)
            team_id_list = self.games_teams_dict[game_id]
            for single_team_id in team_id_list:
                if single_team_id != team_id:
                    team_id = single_team_id
                    break
        if team_id in self.team_stats_dict:
            total_stat = 0.0
            for single_team_stats in self.team_stats_dict[team_id]:
                single_amt = single_team_stats.get(specific_stat)
                if single_amt is None:
                    single_amt = 0.0
                total_stat += single_amt
            total_len = len(self.team_stats_dict[team_id])
            if total_len > 0:
                return total_stat / total_len
        return 0.0

    def get_specific_player_stat_from_games_ago(self, player_stats, specific_stat, games_ago):
        player_id = player_stats.get(PlayerStats.player_id)
        if player_id in self.player_stats_dict and len(self.player_stats_dict[player_id]) >= games_ago:
            return self.player_stats_dict[player_id][games_ago-1].get(specific_stat)
        return 0.0

    def get_avg_player_stat_from_games_ago(self, player_stats, specific_stat, games_ago):
        player_id = player_stats.get(PlayerStats.player_id)
        if player_id in self.player_stats_dict:
            total_stat = 0.0
            game_count = 0
            for single_player_stats in self.player_stats_dict[player_id]:
                single_amt = single_player_stats.get(specific_stat)
                if single_amt is None:
                    single_amt = 0.0
                total_stat += single_amt
                game_count += 1
                if game_count == games_ago:
                    break
            if game_count > 0:
                return total_stat / game_count
        return 0.0

    def add_player_stats_to_dict(self, player_stats):
        player_id = player_stats.get(PlayerStats.player_id)
        if player_id not in self.player_stats_dict:
            self.player_stats_dict[player_id] = [player_stats]
        else:
            self.player_stats_dict[player_id].insert(0, player_stats)

    def add_goalie_stats_to_dict(self, goalie_stats):
        goalie_id = goalie_stats.get(GoalieStats.player_id)
        if goalie_id not in self.goalie_stats_dict:
            self.goalie_stats_dict[goalie_id] = [goalie_stats]
        else:
            self.goalie_stats_dict[goalie_id].insert(0, goalie_stats)
        game_id = goalie_stats.get(GoalieStats.game_id)
        team_id = goalie_stats.get(GoalieStats.team_id)
        if game_id in self.goalie_game_stats_dict:
            if team_id in self.goalie_game_stats_dict[game_id]:
                self.goalie_game_stats_dict[game_id][team_id].append(goalie_stats)
            else:
                self.goalie_game_stats_dict[game_id][team_id] = [goalie_stats]
        else:
            self.goalie_game_stats_dict[game_id] = {team_id: [goalie_stats]}

    def add_team_stats_to_dict(self, game_id):
        team_stats_select = database.entity(TeamStats)
        team_stats_select.add_where(TeamStats.game_id, game_id)
        both_team_stats = self.db_manager.select_all(team_stats_select)
        for single_team_stats in both_team_stats:
            team_id = single_team_stats.get(TeamStats.team_id)
            if team_id not in self.team_stats_dict:
                self.team_stats_dict[team_id] = [single_team_stats]
            else:
                self.team_stats_dict[team_id].insert(0, single_team_stats)

    def add_game(self, game_id):
        games_select = database.entity(Games)
        games_select.add_where(Games.id, game_id)
        both_games = self.db_manager.select_all(games_select)
        team_id_list = []
        for single_game in both_games:
            if single_game.get(Games.is_home):
                self.game_times_dict[game_id] = single_game.get(Games.date_time)
            team_id_list.append(single_game.get(Games.id))
        self.games_teams_dict[game_id] = team_id_list

    def get_player_data(self, player_stats):
        player_id = player_stats.get(PlayerStats.player_id)
        if player_id in self.player_dict:
            return self.player_dict[player_id]
        else:
            player_select = database.entity(Players)
            player_select.add_where(Players.id, player_id)
            player = self.db_manager.select_single(player_select)
            self.player_dict[player_id] = player
            return player

    def get_current_season_year(self):
        if self.current_season_year is None:
            current_season_select = database.entity(Seasons)
            current_season_select.add_where(Seasons.is_current, True)
            current_season = self.db_manager.select_single(current_season_select)
            current_season_id = current_season.get(Seasons.id)
            self.current_season_year = int(str(current_season_id)[:4])
        return self.current_season_year

    def is_same_division(self, first_team_id, second_team_id):
        if len(self.team_division_dict) == 0:
            teams_select = database.entity(Teams)
            teams = self.db_manager.select_all(teams_select)
            for team in teams:
                team_id = team.get(Teams.id)
                division_id = team.get(Teams.division_id)
                self.team_division_dict[team_id] = division_id
        return self.team_division_dict[first_team_id] == self.team_division_dict[second_team_id]

    def is_same_conference(self, first_team_id, second_team_id):
        if len(self.team_conference_dict) == 0:
            teams_select = database.entity(Teams)
            teams = self.db_manager.select_all(teams_select)
            divisions_select = database.entity(Divisions)
            divisions = self.db_manager.select_all(divisions_select)
            for team in teams:
                team_id = team.get(Teams.id)
                division_id = team.get(Teams.division_id)
                for division in divisions:
                    if division.get(Divisions.id) == division_id:
                        conference_id = division.get(Divisions.conference_id)
                        self.team_conference_dict[team_id] = conference_id
                        break
        return self.team_conference_dict[first_team_id] == self.team_conference_dict[second_team_id]

    def get_player_games(self, player_id):
        return len(self.player_stats_dict[player_id])

    def get_opp_goalie_games(self, player_stats):
        goalie_id = self.get_opp_goalie_id_with_most_toi(player_stats)
        return len(self.goalie_stats_dict[goalie_id]) - 1

    def get_team_season_game_count(self, team_id, game_id):
        if team_id in self.team_game_dict:
            if game_id not in self.team_game_dict[team_id]:
                self.team_game_dict[team_id].append(game_id)
            return len(self.team_game_dict[team_id]) - 1
        else:
            self.team_game_dict[team_id] = [game_id]
            return 0

    def get_team_games_since_last_player_game(self, player_stats):
        team_id = player_stats.get(PlayerStats.team_id)
        count = 0
        for team_game_id in reversed(self.team_game_dict[team_id]):
            for single_player_stats in self.player_stats_dict[player_stats.get(PlayerStats.player_id)]:
                if single_player_stats.get(PlayerStats.game_id) == team_game_id:
                    return count
            count += 1
        return 0

    def get_player_season_games_on_team(self, player_stats):
        team_id = player_stats.get(PlayerStats.team_id)
        player_id = player_stats.get(PlayerStats.player_id)
        count = 0
        for single_player_stats in self.player_stats_dict[player_id]:
            if single_player_stats.get(PlayerStats.team_id) == team_id:
                count += 1
        return count

    def get_opp_goalie_id_with_most_toi(self, player_stats):
        opp_team_id = self.get_opp_team_id(player_stats)
        all_goalie_stats_for_game = self.goalie_game_stats_dict[game_id][opp_team_id]
        most_toi_goalie = None
        for single_goalie_game_stats in all_goalie_stats_for_game:
            if most_toi_goalie is None or \
                    single_goalie_game_stats.get(GoalieStats.toi_sec) > most_toi_goalie.get(GoalieStats.toi_sec):
                most_toi_goalie = single_goalie_game_stats
        goalie_id = most_toi_goalie.get(GoalieStats.player_id)
        return goalie_id

    def get_opp_team_id(self, player_stats):
        game_id = player_stats.get(PlayerStats.game_id)
        team_id = player_stats.get(PlayerStats.team_id)
        both_team_ids = self.games_teams_dict[game_id]
        opp_team_id = None
        for single_team_id in both_team_ids:
            if single_team_id != team_id:
                opp_team_id = single_team_id
        return opp_team_id

    def get_days_since_last_team_game(self, player_stats, is_opp=False):
        game_id = player_stats.get(PlayerStats.game_id)
        current_game_time = self.game_times_dict[game_id]
        if is_opp:
            team_id = self.get_opp_team_id(player_stats)
        else:
            team_id = player_stats.get(PlayerStats.team_id)
        if len(self.team_game_dict[team_id]) >= 1:
            previous_game_id = self.team_game_dict[team_id][-1]
            previous_game_time = self.game_times_dict[previous_game_id]
            delta = current_game_time - previous_game_time
            return delta.days
        return 0

    def get_days_since_last_player_game(self, player_stats, is_opp=False):
        game_id = player_stats.get(PlayerStats.game_id)
        current_game_time = self.game_times_dict[game_id]
        if is_opp:
            player_id = self.get_opp_goalie_id_with_most_toi(player_stats)
        else:
            player_id = player_stats.get(PlayerStats.player_id)
        if len(self.player_stats_dict[player_id]) >= 1:
            previous_player_stats = self.player_stats_dict[player_id][0]
            if is_opp:
                previous_game_id = previous_player_stats.get(GoalieStats.game_id)
            else:
                previous_game_id = previous_player_stats.get(PlayerStats.game_id)
            previous_game_time = self.game_times_dict[previous_game_id]
            delta = current_game_time - previous_game_time
            return delta.days
        return 0
