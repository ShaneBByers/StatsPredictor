import logging
import Constants
from datetime import datetime, date
from database import database
from WebSoupManager import WebSoupManager
from Generated.DatabaseClasses import *


class DataManagerFD:

    def __init__(self, logger_name, db_manager):
        self.logger = logging.getLogger(logger_name)

        self.db_manager = db_manager

        self.web_soup_manager = WebSoupManager(logger_name,
                                               Constants.ROTOGRINDERS_URL)

    def current_day_functions(self):
        return

    def get_soup_data(self):
        soup = self.web_soup_manager.get_soup()

        slate_id = self.get_soup_slate(soup)
        games_dict = self.get_soup_games(soup, slate_id)
        self.get_soup_player_stats(games_dict)

    def get_soup_slate(self, soup):
        div = soup.find('div', id='gamestat-filters')
        scr = div.find('script').string
        slate_id = scr.split('Main":{"importId":"')[1].split('"')[0]
        slate = database.entity(FdSlates)
        slate.set(FdSlates.id, slate_id)
        slate.set(FdSlates.date, date.today())
        self.db_manager.insert(slate)
        return slate_id

    def get_soup_games(self, soup, slate_id):
        ul = soup.find('ul', 'lst lineup')
        li_list = ul.find_all('li', attrs={'data-role': 'lineup-card'})

        game_soups_dict = {}
        for li in li_list:
            pitcher_players = li.find('div', 'pitcher players')
            pitcher_input = pitcher_players.find('input')
            pitcher_val = pitcher_input['value']
            if '"slate_id":"' + str(slate_id) + '"' in pitcher_val:
                home_team_abbr = li['data-home']
                fd_home_team = self.get_fd_team_id(home_team_abbr)
                away_team_abbr = li['data-away']
                fd_away_team = self.get_fd_team_id(away_team_abbr)
                fd_game_id = int(li['data-schedule-id'])
                nhl_game_id = self.get_nhl_game_id(fd_home_team.get(FdTeams.nhl_id))
                fd_game_insert = database.entity(FdGames)
                fd_game_insert.set(FdGames.id, fd_game_id)
                fd_game_insert.set(FdGames.slate_id, slate_id)
                fd_game_insert.set(FdGames.home_id, fd_home_team.get(FdTeams.id))
                fd_game_insert.set(FdGames.away_id, fd_away_team.get(FdTeams.id))
                fd_game_insert.set(FdGames.nhl_game_id, nhl_game_id)
                self.db_manager.insert(fd_game_insert)
                game = {'GAME_SOUP': li,
                        'HOME_ID': fd_home_team.get(FdTeams.id),
                        'AWAY_ID': fd_away_team.get(FdTeams.id)}
                game_soups_dict[fd_game_id] = game
        return game_soups_dict

    def get_fd_team_id(self, team_abbr):
        fd_team_select = database.entity(FdTeams)
        fd_team_select.add_where(FdTeams.abbreviation, team_abbr)
        fd_team = self.db_manager.select_single(fd_team_select)
        if fd_team is None:
            fd_team_insert = database.entity(FdTeams)
            fd_team_insert.set(FdTeams.abbreviation, team_abbr)
            nhl_teams_select = database.entity(Teams)
            nhl_teams_select.add_where(Teams.abbreviation, team_abbr)
            nhl_team = self.db_manager.select_single(nhl_teams_select)
            fd_team_insert.set(FdTeams.nhl_id, nhl_team.get(Teams.id))
            self.db_manager.insert(fd_team_insert)
            fd_team = self.db_manager.select_single(fd_team_select)
        return fd_team

    def get_nhl_game_id(self, home_nhl_id):
        nhl_game_select = database.entity(Games)
        select_date = date.today()
        min_time = datetime.min.time()
        max_time = datetime.max.time()
        min_date_time = datetime.combine(select_date, min_time)
        max_date_time = datetime.combine(select_date, max_time)
        nhl_game_select.add_where(Games.date_time, min_date_time, ">")
        nhl_game_select.add_where(Games.date_time, max_date_time, "<")
        nhl_game_select.add_where(Games.team_id, home_nhl_id)
        nhl_game_select.add_where(Games.is_home, True)
        nhl_game = self.db_manager.select_single(nhl_game_select)
        return nhl_game.get(Games.id)

    def get_soup_player_stats(self, games_dict):
        for game_id, game in games_dict.items():
            home_team = game['GAME_SOUP'].find('div', 'blk home-team')
            self.get_soup_player_stats_for_team(home_team, game['HOME_ID'], game_id)
            away_team = game['GAME_SOUP'].find('div', 'blk away-team')
            self.get_soup_player_stats_for_team(away_team, game['AWAY_ID'], game_id)

    def get_soup_player_stats_for_team(self, team, fd_team_id, game_id):
        lines = team.find_all('div', 'blk nhl')
        def_line = 0
        for line in lines:
            line_number = line.find('h4')
            if line_number is not None and "Line " in line_number.string:
                line_number = int(line_number.string.split("Line ")[1])
            else:
                def_line += 1
                line_number = def_line
            line_players = line.find_all('div', 'info')
            for line_player in line_players:
                player = line_player.find('a')
                fd_player_id = self.get_fd_player_id(player)
                select_fd_player_stats = database.entity(FdPlayerStats)
                select_fd_player_stats.add_where(FdPlayerStats.player_id, fd_player_id)
                select_fd_player_stats.add_where(FdPlayerStats.game_id, game_id)
                fd_player_stats = self.db_manager.select_single(select_fd_player_stats)
                if fd_player_stats is None:
                    position = line_player.find('span', 'position').string
                    pp_line = line_player.find('span', 'stats').find('span', 'stats').string
                    if "PP" in pp_line:
                        pp_line = int(pp_line.split("PP")[1])
                    else:
                        pp_line = None
                    salary = line_player.find('span', 'salary').string
                    if "$" in salary and "K" in salary:
                        salary = int(float(salary.split("$")[1].split("K")[0]) * 1000)
                        insert_fd_player_stats = database.entity(FdPlayerStats)
                        insert_fd_player_stats.set(FdPlayerStats.player_id, fd_player_id)
                        insert_fd_player_stats.set(FdPlayerStats.game_id, game_id)
                        insert_fd_player_stats.set(FdPlayerStats.team_id, fd_team_id)
                        insert_fd_player_stats.set(FdPlayerStats.position, position)
                        insert_fd_player_stats.set(FdPlayerStats.line, line_number)
                        insert_fd_player_stats.set(FdPlayerStats.pp_line, pp_line)
                        insert_fd_player_stats.set(FdPlayerStats.salary, salary)
                        self.db_manager.insert(insert_fd_player_stats)

    def get_fd_player_id(self, player):
        fd_player_id = int(player['href'][-5:])
        fd_player_select = database.entity(FdPlayers)
        fd_player_select.add_where(FdPlayers.id, fd_player_id)
        fd_player = self.db_manager.select_single(fd_player_select)
        if fd_player is None:
            player_name = player['title']
            nhl_player_select = database.entity(Players)
            nhl_player_select.add_where(Players.full_name, player_name)
            nhl_player = self.db_manager.select_all(nhl_player_select)
            insert_fd_player = database.entity(FdPlayers)
            insert_fd_player.set(FdPlayers.full_name, player_name)
            insert_fd_player.set(FdPlayers.id, fd_player_id)
            if len(nhl_player) != 1:
                insert_fd_player.set(FdPlayers.nhl_id, None)
            else:
                insert_fd_player.set(FdPlayers.nhl_id, nhl_player[0].get(Players.id))
            self.db_manager.insert(insert_fd_player)
            fd_player = self.db_manager.select_single(fd_player_select)
        return fd_player.get(FdPlayers.id)
