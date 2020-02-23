from enum import Enum


class Conferences(Enum):

    @classmethod
    def table_name(cls):
        return 'CONFERENCES'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'NAME', 'ABBREVIATION', 'SHORT_NAME']

    id = 'ID'
    name = 'NAME'
    abbreviation = 'ABBREVIATION'
    short_name = 'SHORT_NAME'


class Divisions(Enum):

    @classmethod
    def table_name(cls):
        return 'DIVISIONS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'CONFERENCE_ID', 'NAME', 'NAME_SHORT', 'ABBREVIATION']

    id = 'ID'
    conference_id = 'CONFERENCE_ID'
    name = 'NAME'
    name_short = 'NAME_SHORT'
    abbreviation = 'ABBREVIATION'


class FdGames(Enum):

    @classmethod
    def table_name(cls):
        return 'FD_GAMES'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'SLATE_ID', 'HOME_ID', 'AWAY_ID']

    id = 'ID'
    slate_id = 'SLATE_ID'
    home_id = 'HOME_ID'
    away_id = 'AWAY_ID'
    nhl_game_id = 'NHL_GAME_ID'


class FdPlayers(Enum):

    @classmethod
    def table_name(cls):
        return 'FD_PLAYERS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'FULL_NAME']

    id = 'ID'
    full_name = 'FULL_NAME'
    nhl_id = 'NHL_ID'


class FdPlayerStats(Enum):

    @classmethod
    def table_name(cls):
        return 'FD_PLAYER_STATS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['GAME_ID', 'TEAM_ID', 'PLAYER_ID', 'POSITION', 'SALARY']

    game_id = 'GAME_ID'
    team_id = 'TEAM_ID'
    player_id = 'PLAYER_ID'
    position = 'POSITION'
    line = 'LINE'
    pp_line = 'PP_LINE'
    salary = 'SALARY'


class FdScoring(Enum):

    @classmethod
    def table_name(cls):
        return 'FD_SCORING'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['TYPE', 'POINTS']

    type = 'TYPE'
    points = 'POINTS'
    is_goalie = 'IS_GOALIE'


class FdSlates(Enum):

    @classmethod
    def table_name(cls):
        return 'FD_SLATES'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'DATE']

    id = 'ID'
    date = 'DATE'


class FdTeams(Enum):

    @classmethod
    def table_name(cls):
        return 'FD_TEAMS'

    @classmethod
    def auto_increments(cls):
        return ['ID']

    @classmethod
    def not_nulls(cls):
        return ['ABBREVIATION', 'NHL_ID']

    id = 'ID'
    abbreviation = 'ABBREVIATION'
    nhl_id = 'NHL_ID'


class Games(Enum):

    @classmethod
    def table_name(cls):
        return 'GAMES'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'TEAM_ID', 'SEASON_ID', 'IS_HOME', 'DATE_TIME']

    id = 'ID'
    team_id = 'TEAM_ID'
    season_id = 'SEASON_ID'
    is_home = 'IS_HOME'
    date_time = 'DATE_TIME'


class GoaliePredStats(Enum):

    @classmethod
    def table_name(cls):
        return 'GOALIE_PRED_STATS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['GAME_ID', 'TEAM_ID', 'PLAYER_ID']

    game_id = 'GAME_ID'
    team_id = 'TEAM_ID'
    player_id = 'PLAYER_ID'
    saves = 'SAVES'
    ga = 'GA'
    is_win = 'IS_WIN'
    is_shutout = 'IS_SHUTOUT'
    fd_score = 'FD_SCORE'


class GoalieStats(Enum):

    @classmethod
    def table_name(cls):
        return 'GOALIE_STATS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['GAME_ID', 'TEAM_ID', 'PLAYER_ID']

    game_id = 'GAME_ID'
    team_id = 'TEAM_ID'
    player_id = 'PLAYER_ID'
    toi_sec = 'TOI_SEC'
    total_shots = 'TOTAL_SHOTS'
    even_shots = 'EVEN_SHOTS'
    pp_shots = 'PP_SHOTS'
    sh_shots = 'SH_SHOTS'
    total_saves = 'TOTAL_SAVES'
    even_saves = 'EVEN_SAVES'
    pp_saves = 'PP_SAVES'
    sh_saves = 'SH_SAVES'
    decision = 'DECISION'


class Players(Enum):

    @classmethod
    def table_name(cls):
        return 'PLAYERS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'FULL_NAME', 'FIRST_NAME', 'LAST_NAME', 'BIRTH_DATE', 'HEIGHT', 'WEIGHT', 'SHOOTS', 'POSITION']

    id = 'ID'
    full_name = 'FULL_NAME'
    first_name = 'FIRST_NAME'
    last_name = 'LAST_NAME'
    birth_date = 'BIRTH_DATE'
    height = 'HEIGHT'
    weight = 'WEIGHT'
    shoots = 'SHOOTS'
    position = 'POSITION'


class PlayerPredStats(Enum):

    @classmethod
    def table_name(cls):
        return 'PLAYER_PRED_STATS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['GAME_ID', 'TEAM_ID', 'PLAYER_ID']

    game_id = 'GAME_ID'
    team_id = 'TEAM_ID'
    player_id = 'PLAYER_ID'
    goals = 'GOALS'
    assists = 'ASSISTS'
    shots = 'SHOTS'
    ppg = 'PPG'
    ppa = 'PPA'
    shg = 'SHG'
    sha = 'SHA'
    blocked = 'BLOCKED'
    fd_score = 'FD_SCORE'


class PlayerStats(Enum):

    @classmethod
    def table_name(cls):
        return 'PLAYER_STATS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['GAME_ID', 'TEAM_ID', 'PLAYER_ID']

    game_id = 'GAME_ID'
    team_id = 'TEAM_ID'
    player_id = 'PLAYER_ID'
    goals = 'GOALS'
    assists = 'ASSISTS'
    shots = 'SHOTS'
    ppg = 'PPG'
    ppa = 'PPA'
    shg = 'SHG'
    sha = 'SHA'
    pim = 'PIM'
    fot = 'FOT'
    fow = 'FOW'
    hits = 'HITS'
    plus_minus = 'PLUS_MINUS'
    blocked = 'BLOCKED'
    takeaways = 'TAKEAWAYS'
    giveaways = 'GIVEAWAYS'
    toi_sec = 'TOI_SEC'
    pp_toi_sec = 'PP_TOI_SEC'
    sh_toi_sec = 'SH_TOI_SEC'
    even_toi_sec = 'EVEN_TOI_SEC'


class Seasons(Enum):

    @classmethod
    def table_name(cls):
        return 'SEASONS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID']

    id = 'ID'
    start_date = 'START_DATE'
    end_date = 'END_DATE'
    game_amount = 'GAME_AMOUNT'
    is_current = 'IS_CURRENT'


class Teams(Enum):

    @classmethod
    def table_name(cls):
        return 'TEAMS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'DIVISION_ID', 'NAME', 'SHORT_NAME', 'LOCATION_NAME', 'TEAM_NAME', 'ABBREVIATION', 'TIMEZONE_OFFSET']

    id = 'ID'
    division_id = 'DIVISION_ID'
    name = 'NAME'
    short_name = 'SHORT_NAME'
    location_name = 'LOCATION_NAME'
    team_name = 'TEAM_NAME'
    abbreviation = 'ABBREVIATION'
    timezone_offset = 'TIMEZONE_OFFSET'


class TeamStats(Enum):

    @classmethod
    def table_name(cls):
        return 'TEAM_STATS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['GAME_ID', 'TEAM_ID', 'PP']

    game_id = 'GAME_ID'
    team_id = 'TEAM_ID'
    goals = 'GOALS'
    shots = 'SHOTS'
    pp = 'PP'
    ppg = 'PPG'
    pim = 'PIM'
    blocked = 'BLOCKED'
    takeaways = 'TAKEAWAYS'
    giveaways = 'GIVEAWAYS'
    hits = 'HITS'


class TranslationColumns(Enum):

    @classmethod
    def table_name(cls):
        return 'TRANSLATION_COLUMNS'

    @classmethod
    def auto_increments(cls):
        return ['ID']

    @classmethod
    def not_nulls(cls):
        return ['TABLE_ID', 'REF_COLUMN']

    id = 'ID'
    table_id = 'TABLE_ID'
    group_id = 'GROUP_ID'
    ref_column = 'REF_COLUMN'
    modifier = 'MODIFIER'
    immediate = 'IMMEDIATE'


class TranslationGroups(Enum):

    @classmethod
    def table_name(cls):
        return 'TRANSLATION_GROUPS'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'VALUE_NO', 'IS_URL']

    id = 'ID'
    value_no = 'VALUE_NO'
    value = 'VALUE'
    is_url = 'IS_URL'


class TranslationTables(Enum):

    @classmethod
    def table_name(cls):
        return 'TRANSLATION_TABLES'

    @classmethod
    def auto_increments(cls):
        return ['ID']

    @classmethod
    def not_nulls(cls):
        return ['REF_TABLE', 'IS_SINGLE']

    id = 'ID'
    ref_table = 'REF_TABLE'
    url_path = 'URL_PATH'
    modifier = 'MODIFIER'
    is_single = 'IS_SINGLE'


class TranslationValues(Enum):

    @classmethod
    def table_name(cls):
        return 'TRANSLATION_VALUES'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['COLUMN_ID', 'VALUE_NO', 'IS_URL']

    column_id = 'COLUMN_ID'
    value_no = 'VALUE_NO'
    value = 'VALUE'
    is_url = 'IS_URL'


DB_TABLES = {'CONFERENCES': Conferences,
             'DIVISIONS': Divisions,
             'FD_GAMES': FdGames,
             'FD_PLAYERS': FdPlayers,
             'FD_PLAYER_STATS': FdPlayerStats,
             'FD_SCORING': FdScoring,
             'FD_SLATES': FdSlates,
             'FD_TEAMS': FdTeams,
             'GAMES': Games,
             'GOALIE_PRED_STATS': GoaliePredStats,
             'GOALIE_STATS': GoalieStats,
             'PLAYERS': Players,
             'PLAYER_PRED_STATS': PlayerPredStats,
             'PLAYER_STATS': PlayerStats,
             'SEASONS': Seasons,
             'TEAMS': Teams,
             'TEAM_STATS': TeamStats,
             'TRANSLATION_COLUMNS': TranslationColumns,
             'TRANSLATION_GROUPS': TranslationGroups,
             'TRANSLATION_TABLES': TranslationTables,
             'TRANSLATION_VALUES': TranslationValues}
