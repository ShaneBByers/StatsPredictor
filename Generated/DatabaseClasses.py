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


class Games(Enum):

    @classmethod
    def table_name(cls):
        return 'GAMES'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['ID', 'HOME_TEAM_ID', 'AWAY_TEAM_ID', 'DATE_TIME']

    id = 'ID'
    home_team_id = 'HOME_TEAM_ID'
    away_team_id = 'AWAY_TEAM_ID'
    date_time = 'DATE_TIME'


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
        return ['REF_TABLE']

    id = 'ID'
    ref_table = 'REF_TABLE'
    url_path = 'URL_PATH'
    modifier = 'MODIFIER'


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
             'GAMES': Games,
             'PLAYERS': Players,
             'SEASONS': Seasons,
             'TEAMS': Teams,
             'TRANSLATION_COLUMNS': TranslationColumns,
             'TRANSLATION_GROUPS': TranslationGroups,
             'TRANSLATION_TABLES': TranslationTables,
             'TRANSLATION_VALUES': TranslationValues}
