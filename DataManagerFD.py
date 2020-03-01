import logging
import Constants
from datetime import datetime, date
from database import database
from WebSoupManager import WebSoupManager
from Generated.DatabaseClasses import *


class DataManagerFD:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)

        self.db_manager = db_manager

        self.web_soup_manager = WebSoupManager(Constants.ROTOGRINDERS_URL)

    def current_day_functions(self):
        self.logger.info("RUNNING CURRENT DAY FUNCTIONS FOR FD")
        soup = self.web_soup_manager.get_soup()

        slate_id = self.get_soup_slate(soup)
        if slate_id is not None:
            self.logger.debug("Got SLATE with ID " + str(slate_id))
            games_dict = self.get_soup_games(soup, slate_id)
            self.get_soup_player_stats(games_dict)
        self.db_manager.commit()

    def get_soup_slate(self, soup):
        self.logger.debug("Attempting to get SLATE")
        div = soup.find('div', id='gamestat-filters')
        scr = div.find('script').string
        slate_id = scr.split('Main":{"importId":"')[1].split('"')[0]
        self.logger.debug("Found SLATE with ID " + str(slate_id) + " in soup")
        select_slate = database.entity(FdSlates)
        select_slate.add_where(FdSlates.id, slate_id)
        slate = self.db_manager.select_single(select_slate)
        if slate is None:
            insert_slate = database.entity(FdSlates)
            insert_slate.set(FdSlates.id, slate_id)
            insert_slate.set(FdSlates.date, date.today())
            self.db_manager.insert(insert_slate, commit=False)
            self.logger.info("Successfully inserted SLATE with ID " + str(slate_id) + " into DB")
            return slate_id
        else:
            self.logger.info("DB already contains SLATE with ID " + str(slate_id))
            return None

    def get_soup_games(self, soup, slate_id):
        self.logger.debug("Attempting to get FD_GAMES for SLATE with ID " + str(slate_id))
        ul = soup.find('ul', 'lst lineup')
        li_list = ul.find_all('li', attrs={'data-role': 'lineup-card'})

        game_soups_dict = {}
        for li in li_list:
            in_slate = False
            pitcher_players_list = li.find_all('div', 'pitcher players')
            for pitcher_players in pitcher_players_list:
                pitcher_input = pitcher_players.find('input')
                pitcher_val = pitcher_input['value']
                if '"slate_id":"' + str(slate_id) + '"' in pitcher_val:
                    in_slate = True
                    break
            if in_slate:
                home_team_abbr = li['data-home']
                fd_home_team = self.get_fd_team_id(home_team_abbr)
                away_team_abbr = li['data-away']
                self.logger.info("Found game between " +
                                 home_team_abbr +
                                 " and " +
                                 away_team_abbr +
                                 " for slate with ID " +
                                 str(slate_id))
                fd_away_team = self.get_fd_team_id(away_team_abbr)
                fd_game_id = int(li['data-schedule-id'])
                nhl_game_id = self.get_nhl_game_id(fd_home_team.get(FdTeams.nhl_id))
                fd_game_insert = database.entity(FdGames)
                fd_game_insert.set(FdGames.id, fd_game_id)
                fd_game_insert.set(FdGames.slate_id, slate_id)
                fd_game_insert.set(FdGames.home_id, fd_home_team.get(FdTeams.id))
                fd_game_insert.set(FdGames.away_id, fd_away_team.get(FdTeams.id))
                fd_game_insert.set(FdGames.nhl_game_id, nhl_game_id)
                self.db_manager.insert(fd_game_insert, commit=False)
                game = {'GAME_SOUP': li,
                        'HOME_ID': fd_home_team.get(FdTeams.id),
                        'AWAY_ID': fd_away_team.get(FdTeams.id)}
                game_soups_dict[fd_game_id] = game
        return game_soups_dict

    def get_fd_team_id(self, team_abbr):
        self.logger.debug("Attempting to get FD_TEAM from abbreviation " + team_abbr)
        fd_team_select = database.entity(FdTeams)
        fd_team_select.add_where(FdTeams.abbreviation, team_abbr)
        fd_team = self.db_manager.select_single(fd_team_select)
        if fd_team is None:
            self.logger.warning("DB does not contain FD_TEAM with abbreviation " + team_abbr)
            fd_team_insert = database.entity(FdTeams)
            fd_team_insert.set(FdTeams.abbreviation, team_abbr)
            nhl_teams_select = database.entity(Teams)
            nhl_teams_select.add_where(Teams.abbreviation, team_abbr)
            nhl_team = self.db_manager.select_single(nhl_teams_select)
            self.logger.info("Found NHL team with matching abbreviation with ID " + str(nhl_team.get(Teams.id)))
            fd_team_insert.set(FdTeams.nhl_id, nhl_team.get(Teams.id))
            self.db_manager.insert(fd_team_insert, commit=False)
            fd_team = self.db_manager.select_single(fd_team_select)
        self.logger.info("Found FD_TEAM with ID " + str(fd_team.get(FdTeams.id)))
        return fd_team

    def get_nhl_game_id(self, home_nhl_id):
        self.logger.debug("Attempting to get NHL_GAME from TEAM at home with ID " + str(home_nhl_id))
        nhl_game_select = database.entity(Games)
        select_date = date.today()
        min_time = datetime.min.time()
        max_time = datetime.max.time()
        min_date_time = datetime.combine(select_date, min_time)
        max_date_time = datetime.combine(select_date, max_time)
        self.logger.debug("Finding game between " +
                          str(min_date_time) +
                          " and " +
                          str(max_date_time))
        nhl_game_select.add_where(Games.date_time, min_date_time, ">")
        nhl_game_select.add_where(Games.date_time, max_date_time, "<")
        nhl_game_select.add_where(Games.team_id, home_nhl_id)
        nhl_game_select.add_where(Games.is_home, True)
        nhl_game = self.db_manager.select_single(nhl_game_select)
        self.logger.info("Found NHL_GAME with ID " + str(nhl_game.get(Games.id)))
        return nhl_game.get(Games.id)

    def get_soup_player_stats(self, games_dict):
        for game_id, game in games_dict.items():
            home_team = game['GAME_SOUP'].find('div', 'blk home-team')
            self.get_soup_player_stats_for_team(home_team, game['HOME_ID'], game_id)
            away_team = game['GAME_SOUP'].find('div', 'blk away-team')
            self.get_soup_player_stats_for_team(away_team, game['AWAY_ID'], game_id)

    def get_soup_player_stats_for_team(self, team, fd_team_id, game_id):
        self.logger.info("Getting FD_PLAYER_STATS for FD_TEAM with ID " +
                         str(fd_team_id) +
                         " and NHL_GAME with ID " +
                         str(game_id))
        pitcher_player = team.find('div', 'pitcher players')
        goalie = pitcher_player.find('a')
        fd_player_id = self.get_fd_player_id(goalie)
        salary = pitcher_player.find('span', 'meta stats').find('span', 'salary').string
        if "$" in salary and "K" in salary:
            self.logger.debug("Inserting goalie FD_PLAYER_STATS with PLAYER_ID " + str(fd_player_id))
            salary = int(float(salary.split("$")[1].split("K")[0]) * 1000)
            insert_fd_player_stats = database.entity(FdPlayerStats)
            insert_fd_player_stats.set(FdPlayerStats.player_id, fd_player_id)
            insert_fd_player_stats.set(FdPlayerStats.game_id, game_id)
            insert_fd_player_stats.set(FdPlayerStats.team_id, fd_team_id)
            insert_fd_player_stats.set(FdPlayerStats.position, "G")
            insert_fd_player_stats.set(FdPlayerStats.line, None)
            insert_fd_player_stats.set(FdPlayerStats.pp_line, None)
            insert_fd_player_stats.set(FdPlayerStats.salary, salary)
            self.db_manager.insert(insert_fd_player_stats, commit=False)
        else:
            self.logger.warning("Invalid salary value for goalie FD_PLAYER with ID " + str(fd_player_id))
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
                self.logger.debug("Found player FD_PLAYER with ID " + str(fd_player_id))
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
                        self.logger.debug("Inserting player FD_PLAYER_STATS with PLAYER_ID " + str(fd_player_id))
                        salary = int(float(salary.split("$")[1].split("K")[0]) * 1000)
                        insert_fd_player_stats = database.entity(FdPlayerStats)
                        insert_fd_player_stats.set(FdPlayerStats.player_id, fd_player_id)
                        insert_fd_player_stats.set(FdPlayerStats.game_id, game_id)
                        insert_fd_player_stats.set(FdPlayerStats.team_id, fd_team_id)
                        insert_fd_player_stats.set(FdPlayerStats.position, position)
                        insert_fd_player_stats.set(FdPlayerStats.line, line_number)
                        insert_fd_player_stats.set(FdPlayerStats.pp_line, pp_line)
                        insert_fd_player_stats.set(FdPlayerStats.salary, salary)
                        self.db_manager.insert(insert_fd_player_stats, commit=False)
                    else:
                        self.logger.warning("Invalid salary value for player FD_PLAYER with ID " + str(fd_player_id))
                else:
                    self.logger.warning("DB already contains FD_PLAYER_STATS for player with ID " + str(fd_player_id))

    def get_fd_player_id(self, player):
        self.logger.info("Attempting to get FD_PLAYER from soup player")
        last_hyphen = player['href'].rfind('-')
        fd_player_id = int(player['href'][last_hyphen + 1:])
        fd_player_select = database.entity(FdPlayers)
        fd_player_select.add_where(FdPlayers.id, fd_player_id)
        fd_player = self.db_manager.select_single(fd_player_select)
        if fd_player is None:
            self.logger.info("DB does not contain FD_PLAYER with ID " + str(fd_player_id))
            if 'title' in player.attrs:
                player_name = player['title']
            else:
                player_name = player.string
            nhl_player_select = database.entity(Players)
            nhl_player_select.add_where(Players.full_name, player_name)
            nhl_player = self.db_manager.select_all(nhl_player_select)
            insert_fd_player = database.entity(FdPlayers)
            insert_fd_player.set(FdPlayers.full_name, player_name)
            insert_fd_player.set(FdPlayers.id, fd_player_id)
            if len(nhl_player) != 1:
                self.logger.warning("Could not find single NHL_PLAYER match for " + player_name)
                insert_fd_player.set(FdPlayers.nhl_id, None)
            else:
                self.logger.info("Found NHL player with ID " + str(nhl_player[0].get(Players.id)))
                insert_fd_player.set(FdPlayers.nhl_id, nhl_player[0].get(Players.id))
            self.db_manager.insert(insert_fd_player, commit=False)
            fd_player = self.db_manager.select_single(fd_player_select)
        self.logger.debug("Found FD_PLAYER with ID " + str(fd_player.get(FdPlayers.id)))
        return fd_player.get(FdPlayers.id)
