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
    ref_column = 'REF_COLUMN'


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


class TranslationValues(Enum):

    @classmethod
    def table_name(cls):
        return 'TRANSLATION_VALUES'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return ['COLUMN_ID', 'VALUE_NO']

    column_id = 'COLUMN_ID'
    value_no = 'VALUE_NO'
    value = 'VALUE'


DB_TABLES = {'CONFERENCES': Conferences,
             'DIVISIONS': Divisions,
             'TEAMS': Teams,
             'TRANSLATION_COLUMNS': TranslationColumns,
             'TRANSLATION_TABLES': TranslationTables,
             'TRANSLATION_VALUES': TranslationValues}
