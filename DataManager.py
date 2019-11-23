import logging
import Constants
from database import database
from WebManager import WebManager
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
        else:
            self.web_manager = None

    def update_classes_file(self, file_name):
        self.db_manager.update_classes_file(file_name)

    def insert_teams(self):
        self.insert_from_web("TEAMS")

    def insert_players(self):
        self.insert_from_web("PLAYERS")

    def insert_from_web(self, table_name):
        translation_table, translations = self.get_translations(DB_TABLES[table_name])
        json = self.web_manager.get(translation_table.get(TranslationTables.url_path))
        parse_values = {}
        for col, values in translations.items():
            web_values = self.parse_json(json, values, 1)
            parse_values[col.get(TranslationColumns.ref_column)] = web_values
        insert_values = None
        for parse_index, parse_value in parse_values.items():
            if insert_values is None:
                insert_values = []
                for _ in parse_value:
                    insert_values.append(database.entity(DB_TABLES[table_name]))
            for col_name in DB_TABLES[table_name]:
                if col_name.value == parse_index:
                    for val_index in range(len(parse_value)):
                        insert_values[val_index].set(col_name, parse_value[val_index])
        self.db_manager.insert(insert_values)

    def parse_json(self, json, translations, translation_counter):
        translation_index = translation_counter - 1
        if translation_index >= len(translations):
            return json
        else:
            if translations[translation_index].get(TranslationValues.value) is None:
                return_values = []
                for json_value in json:
                    return_values.append(self.parse_json(json_value, translations, translation_counter + 1))
                return return_values
            else:
                new_json = json[translations[translation_index].get(TranslationValues.value)]
                return self.parse_json(new_json, translations, translation_counter + 1)

    def get_translations(self, table):
        translation_table = self.get_translation_table(table)
        translation_columns = self.get_translation_columns(translation_table.get(TranslationTables.id))
        translations = {}
        for col in translation_columns:
            translations[col] = self.get_translation_values(col.get(TranslationColumns.id))
        return_value = (translation_table, translations)
        return return_value

    def get_translation_table(self, table):
        translation_table_select = database.entity(TranslationTables)
        translation_table_select.add_where(TranslationTables.ref_table, table.table_name())
        return self.db_manager.select_single(translation_table_select)

    def get_translation_columns(self, table_id):
        translation_column_select = database.entity(TranslationColumns)
        translation_column_select.add_where(TranslationColumns.table_id, table_id)
        return self.db_manager.select_all(translation_column_select)

    def get_translation_values(self, column_id):
        translation_value_select = database.entity(TranslationValues)
        translation_value_select.add_where(TranslationValues.column_id, column_id)
        translation_value_select.add_order_by(TranslationValues.value_no)
        return self.db_manager.select_all(translation_value_select)
