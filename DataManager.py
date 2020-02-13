import logging
import Constants
from datetime import timedelta, date, datetime
from database import database
from WebManager import WebManager
from WebSoupManager import WebSoupManager
from Modifiers import Modifier
from Generated.DatabaseClasses import *


class DataManager:

    def __init__(self, logger_name, db=True, web=True):
        self.logger = logging.getLogger(logger_name)

        if db:
            self.db_manager = database.connect(logger_name,
                                               Constants.DB_HOST,
                                               Constants.DB_USERNAME,
                                               Constants.DB_PASSWORD,
                                               Constants.DB_NAME)
        else:
            self.db_manager = None

        if web:
            self.web_manager = WebManager(logger_name,
                                          Constants.WEB_BASE_URL)
            self.web_soup_manager = WebSoupManager(logger_name,
                                                   Constants.ROTOGRINDERS_URL,
                                                   False)
        else:
            self.web_manager = None
            self.web_soup_manager = None

        self.modifier = Modifier(logger_name,
                                 self.db_manager)

    def update_classes_file(self, file_name):
        self.db_manager.update_classes_file(file_name)

    def insert_teams(self):
        insert_values = self.get_web_values("TEAMS")
        self.db_manager.insert(insert_values)

    def insert_players(self):
        insert_values = self.get_web_values("PLAYERS")
        self.db_manager.insert(insert_values)

    def insert_seasons(self):
        insert_values = self.get_web_values("SEASONS")
        self.db_manager.insert(insert_values)

    def insert_games(self, current_season=True, season_id=None):
        season_select = database.entity(Seasons)
        if current_season:
            season_select.add_where(Seasons.is_current, True)
        elif season_id is not None:
            season_select.add_where(Seasons.id, season_id)
        season = self.db_manager.select_single(season_select)
        start_date = self.modifier.date_to_date_string(season.get(Seasons.start_date))
        end_date = self.modifier.date_to_date_string(season.get(Seasons.end_date))
        season_id = season.get(Seasons.id)
        insert_values = self.get_web_values("GAMES", [start_date, end_date], {"SEASON_ID": season_id})
        teams = self.db_manager.select_all(database.entity(Teams))
        team_ids = []
        for team in teams:
            team_ids.append(team.get(Teams.id))
        remove_game_ids = []
        for insert_value in insert_values:
            if insert_value.get(Games.team_id) not in team_ids:
                remove_game_ids.append(insert_value.get(Games.id))
        remove_games = []
        for remove_game_id in remove_game_ids:
            for insert_value in insert_values:
                if remove_game_id == insert_value.get(Games.id):
                    remove_games.append(insert_value)
        for remove_game in remove_games:
            insert_values.remove(remove_game)
        self.db_manager.insert(insert_values)

    def insert_team_stats(self, current_season=True, season_id=None, games=None):
        if games is None:
            season_select = database.entity(Seasons)
            if current_season:
                season_select.add_where(Seasons.is_current, True)
            elif season_id is not None:
                season_select.add_where(Seasons.id, season_id)
            season = self.db_manager.select_single(season_select)
            games_select = database.entity(Games)
            games_select.add_where(Games.season_id, season.get(Seasons.id))
            games_select.add_where(Games.is_home, True)
            games = self.db_manager.select_all(games_select)
        insert_values = []
        translations_dict = self.get_translations(DB_TABLES["TEAM_STATS"])
        today = date.today()
        for game in games:
            game_date = game.get(Games.date_time).date()
            if game_date < today:
                insert_values.extend(self.get_web_values("TEAM_STATS",
                                                         modify_args=(game.get(Games.id)),
                                                         additional_vals=None,
                                                         translations_dict=translations_dict))
        self.db_manager.insert(insert_values)

    def insert_player_stats(self, current_season=True, season_id=None, games=None):
        if games is None:
            season_select = database.entity(Seasons)
            if current_season:
                season_select.add_where(Seasons.is_current, True)
            elif season_id is not None:
                season_select.add_where(Seasons.id, season_id)
            season = self.db_manager.select_single(season_select)
            games_select = database.entity(Games)
            games_select.add_where(Games.season_id, season.get(Seasons.id))
            games_select.add_where(Games.is_home, True)
            games = self.db_manager.select_all(games_select)
        insert_values = []
        translations_dict = self.get_translations(DB_TABLES["PLAYER_STATS"])
        today = date.today()
        for game in games:
            game_date = game.get(Games.date_time).date()
            if game_date < today:
                insert_values.extend(self.get_web_values("PLAYER_STATS",
                                                         modify_args=(game.get(Games.id)),
                                                         additional_vals={"GAME_ID": game.get(Games.id)},
                                                         translations_dict=translations_dict))
        current_players_select = database.entity(Players)
        current_players = self.db_manager.select_all(current_players_select)
        current_player_ids = list(map(lambda x: x.get(Players.id), current_players))
        insert_new_player_ids = []
        for insert_value in insert_values:
            insert_value_id = insert_value.get(PlayerStats.player_id)
            if insert_value_id not in current_player_ids and insert_value_id not in insert_new_player_ids:
                insert_new_player_ids.append(insert_value_id)
        if len(insert_new_player_ids) > 0:
            insert_new_players = []
            new_player_translation_dict = self.get_translations(DB_TABLES["PLAYERS"], True)
            for insert_new_player_id in insert_new_player_ids:
                insert_new_players.extend(self.get_web_values("PLAYERS",
                                                              modify_args=insert_new_player_id,
                                                              translations_dict=new_player_translation_dict))
            self.db_manager.insert(insert_new_players, False)
        self.db_manager.insert(insert_values)

    def update_game_times(self, season_id=None):
        games_select = database.entity(Games)
        games_select.add_where(Games.is_home, True)
        if season_id is not None:
            games_select.add_where(Games.season_id, season_id)
        games = self.db_manager.select_all(games_select)
        teams_select = database.entity(Teams)
        teams = self.db_manager.select_all(teams_select)
        teams_dict = {}
        for team in teams:
            teams_dict[team.get(Teams.id)] = team.get(Teams.timezone_offset)
        for game in games:
            game_start = game.get(Games.date_time)
            offset = teams_dict[game.get(Games.team_id)]
            game_start += timedelta(hours=offset)
            game.set(Games.date_time, game_start)
            game.add_where(Games.id, game.get(Games.id))
        self.db_manager.update(games)

    def full_season(self, season_id):
        self.insert_games(current_season=False,
                          season_id=season_id)
        self.update_game_times(season_id=season_id)
        self.insert_team_stats(current_season=False,
                               season_id=season_id)
        self.insert_player_stats(current_season=False,
                                 season_id=season_id)

    def current_day_functions(self):
        team_stats_select = database.entity(TeamStats)
        team_stats_select.add_order_by(TeamStats.game_id, False)
        team_stats = self.db_manager.select_single(team_stats_select)
        last_game_id = team_stats.get(TeamStats.game_id)
        last_game_select = database.entity(Games)
        last_game_select.add_where(Games.id, last_game_id)
        last_game_select.add_where(Games.is_home, True)
        last_game = self.db_manager.select_single(last_game_select)
        last_date = last_game.get(Games.date_time).date()
        season_select = database.entity(Seasons)
        season_select.add_where(Seasons.is_current, True)
        season = self.db_manager.select_single(season_select)
        season_games_select = database.entity(Games)
        season_games_select.add_where(Games.season_id, season.get(Seasons.id))
        season_games_select.add_where(Games.is_home, True)
        season_games = self.db_manager.select_all(season_games_select)
        today = date.today()
        games_filter = filter(lambda x: last_date < x.get(Games.date_time).date() < today, season_games)
        selected_games = list(games_filter)
        self.insert_team_stats(games=selected_games)
        self.insert_player_stats(games=selected_games)

    def get_web_values(self, table_name, modify_args=None, additional_vals=None, translations_dict=None):
        return_values = []
        if translations_dict is None:
            translations_dict = self.get_translations(DB_TABLES[table_name])
        for translation_table, translations in translations_dict.items():
            if modify_args is None:
                json = self.web_manager.get(translation_table.get(TranslationTables.url_path))
            else:
                new_get = translation_table.get(TranslationTables.url_path)
                new_get = self.modifier.modify(translation_table.get(TranslationTables.modifier), (new_get, modify_args))
                json = self.web_manager.get(new_get)
            all_groups_web_values = []
            for group_id, translations_tuple in translations.items():
                result = self.parse_json(json, translations_tuple, 1, 0)
                if not isinstance(result, list):
                    result = [result]
                all_groups_web_values.append(result)
            longest_index = 0
            if len(all_groups_web_values) > 1:
                for i in range(len(all_groups_web_values)):
                    if len(all_groups_web_values[i]) > len(all_groups_web_values[longest_index]):
                        longest_index = i
                for i in range(len(all_groups_web_values)):
                    if i != longest_index:
                        for j in range(len(all_groups_web_values[longest_index])):
                            for k in range(len(all_groups_web_values[i])):
                                all_groups_web_values[longest_index][j].update(all_groups_web_values[i][k])
            web_values = all_groups_web_values[longest_index]
            if additional_vals is not None:
                for web_value in web_values:
                    web_value.update(additional_vals)
            for web_value in web_values:
                insert_value = database.entity(DB_TABLES[table_name])
                for col_name in DB_TABLES[table_name]:
                    if col_name.value in web_value:
                        insert_value.set(col_name, web_value[col_name.value])
                return_values.append(insert_value)
        return return_values

    def parse_json(self, json, translations, group_counter, value_counter, col_entity=None):
        if group_counter <= len(translations[0]):
            translation_index = group_counter - 1
            group_counter += 1
            after_group = False
        elif value_counter == 0 or value_counter <= len(translations[1][col_entity]):
            translation_index = value_counter - 1
            value_counter += 1
            after_group = True
        else:
            if col_entity.get(TranslationColumns.modifier) is None:
                return json
            else:
                return self.modifier.modify(col_entity.get(TranslationColumns.modifier), json)

        if group_counter == len(translations[0]) + 1 and value_counter == 1:
            return_dict = {}
            for col in translations[1].keys():
                if col.get(TranslationColumns.immediate) is not None:
                    result = self.modifier.immediate(col.get(TranslationColumns.immediate))
                else:
                    result = self.parse_json(json, translations, group_counter, value_counter, col)
                if result is not None:
                    return_dict[col.get(TranslationColumns.ref_column)] = result
            return return_dict
        else:
            entity_list = translations[after_group]
            if col_entity is not None:
                entity_list = entity_list[col_entity]
            if entity_list[translation_index].get(TranslationValues.value) is None:
                return_values = []
                if isinstance(json, dict):
                    json = list(json.values())
                for json_value in json:
                    inner_result = self.parse_json(json_value, translations, group_counter, value_counter, col_entity)
                    if inner_result is not None:
                        if isinstance(inner_result, list):
                            return_values.extend(inner_result)
                        else:
                            return_values.append(inner_result)
                longest_length = 0
                for i in range(len(return_values)):
                    if len(return_values[i]) > longest_length:
                        longest_length = len(return_values[i])
                new_return_values = []
                for return_val in return_values:
                    if len(return_val) == longest_length:
                        new_return_values.append(return_val)
                return_values = new_return_values
                return return_values
            elif entity_list[translation_index].get(TranslationValues.is_url):
                url_var = self.modifier.replace_string(entity_list[translation_index].get(TranslationValues.value),
                                                       str(json))
                new_json = self.web_manager.get(url_var)
                return self.parse_json(new_json, translations, group_counter, value_counter, col_entity)
            else:
                search_value = entity_list[translation_index].get(TranslationValues.value)
                if search_value in json:
                    new_json = json[entity_list[translation_index].get(TranslationValues.value)]
                    return self.parse_json(new_json, translations, group_counter, value_counter, col_entity)
                else:
                    return None

    def get_translations(self, table, is_single=False):
        translation_tables = self.get_translation_tables(table, is_single)
        return_translations = {}
        for translation_table in translation_tables:
            translation_columns = self.get_translation_columns(translation_table.get(TranslationTables.id))
            translations = {}
            for col in translation_columns:
                new_group_id = col.get(TranslationColumns.group_id)
                if new_group_id not in translations:
                    group_values = self.get_translation_group_values(new_group_id)
                    col_values = {col: self.get_translation_values(col.get(TranslationColumns.id))}
                    translations[new_group_id] = (group_values, col_values)
                else:
                    col_values = translations[new_group_id][1]
                    col_values[col] = self.get_translation_values(col.get(TranslationColumns.id))
                    translations[new_group_id] = (translations[new_group_id][0], col_values)
            return_translations[translation_table] = translations

        return return_translations

    def get_translation_tables(self, table, is_single=False):
        translation_table_select = database.entity(TranslationTables)
        translation_table_select.add_where(TranslationTables.ref_table, table.table_name())
        translation_table_select.add_where(TranslationTables.is_single, is_single)
        return self.db_manager.select_all(translation_table_select)

    def get_translation_columns(self, table_id):
        translation_column_select = database.entity(TranslationColumns)
        translation_column_select.add_where(TranslationColumns.table_id, table_id)
        return self.db_manager.select_all(translation_column_select)

    def get_translation_group_values(self, group_id):
        translation_group_select = database.entity(TranslationGroups)
        translation_group_select.add_where(TranslationGroups.id, group_id)
        return self.db_manager.select_all(translation_group_select)

    def get_translation_values(self, column_id):
        translation_value_select = database.entity(TranslationValues)
        translation_value_select.add_where(TranslationValues.column_id, column_id)
        translation_value_select.add_order_by(TranslationValues.value_no)
        return self.db_manager.select_all(translation_value_select)

    def get_soup_data(self):
        soup = self.web_soup_manager.get_soup()

        slate_id = self.get_soup_slate(soup)
        games_dict = self.get_soup_games(soup, slate_id)
        self.get_soup_player_stats(games_dict)

        # ul = soup.find('ul', 'lst lineup')
        # li_list = ul.find_all('li', attrs={'data-role': 'lineup-card'})
        #
        # for li in li_list:
        #     away_team_name = li['data-away']
        #     home_team_name = li['data-home']
        #     away_team = li.find('div', 'blk away-team')
        #     away_lines = away_team.find_all('div', 'blk nhl')
        #     for away_line in away_lines:
        #         line_number = away_line.find('h4').string
        #         line_players = away_line.find_all('div', 'info')
        #         for line_player in line_players:
        #             player = line_player.find('a')
        #             player_id = player['href'][-5:]
        #             player_name = player['title']
        #             position = line_player.find('span', 'position').string
        #             extra = line_player.find('span', 'stats').find('span', 'stats').string
        #             salary = line_player.find('span', 'salary').string

    def get_soup_slate(self, soup):
        div = soup.find('div', id='gamestat-filters')
        scr = div.find('script').string
        slate_id = scr.split('Main":{"importId":"')[1].split('"')[0]
        slate = database.entity(FdSlates)
        slate.set(FdSlates.id, slate_id)
        slate.set(FdSlates.date, date.today())
        # self.db_manager.insert(slate)
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
                fd_game_id = li['data-schedule-id']
                nhl_game_id = self.get_nhl_game_id(fd_home_team.get(FdTeams.nhl_id))
                fd_game_insert = database.entity(FdGames)
                fd_game_insert.set(FdGames.id, fd_game_id)
                fd_game_insert.set(FdGames.slate_id, slate_id)
                fd_game_insert.set(FdGames.home_id, fd_home_team.get(FdTeams.id))
                fd_game_insert.set(FdGames.away_id, fd_away_team.get(FdTeams.id))
                fd_game_insert.set(FdGames.nhl_game_id, nhl_game_id)
                # self.db_manager.insert(fd_game_insert)
                game_soups_dict[fd_game_id] = li
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
            # self.db_manager.insert(fd_team_insert)
            fd_team = self.db_manager.select_single(fd_team_select)
        return fd_team

    def get_nhl_game_id(self, home_nhl_id):
        nhl_game_select = database.entity(Games)
        select_date = date(2020, 2, 9)
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
        for game_id, game in games_dict.values():
            home_team = game.find('div', 'blk home-team')
            home_lines = home_team.find_all('div', 'blk nhl')
            for home_line in home_lines:
                line_number = home_line.find('h4').string
                line_players = home_line.find_all('div', 'info')
                for line_player in line_players:
                    player = line_player.find('a')
                    player_id = player['href'][-5:]
                    player_name = player['title']
                    position = line_player.find('span', 'position').string
                    extra = line_player.find('span', 'stats').find('span', 'stats').string
                    salary = line_player.find('span', 'salary').string