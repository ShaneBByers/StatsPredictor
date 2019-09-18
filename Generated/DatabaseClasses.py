from enum import Enum


class Testing(Enum):

    @classmethod
    def table_name(cls):
        return 'TESTING'

    @classmethod
    def auto_increments(cls):
        return []

    @classmethod
    def not_nulls(cls):
        return []

    test = 'TEST'
