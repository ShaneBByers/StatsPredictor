import logging
import Constants
import Modifiers
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
        all_groups_web_values = []
        for group_id, translations_tuple in translations.items():
            all_groups_web_values.append(self.parse_json(json, translations_tuple, 1, 0))
        if len(all_groups_web_values) > 1:
            for i in range(len(all_groups_web_values)):
                if i != 0:
                    for j in range(len(all_groups_web_values[0])):
                        all_groups_web_values[0][j].update(all_groups_web_values[i][j])
        web_values = all_groups_web_values[0]
        insert_values = []
        for web_value in web_values:
            insert_value = database.entity(DB_TABLES[table_name])
            for col_name in DB_TABLES[table_name]:
                if col_name.value in web_value:
                    insert_value.set(col_name, web_value[col_name.value])
            insert_values.append(insert_value)
        self.db_manager.insert(insert_values)

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
                return Modifiers.modifiers[col_entity.get(TranslationColumns.modifier)](json)

        if group_counter == len(translations[0]) + 1 and value_counter == 1:
            return_dict = {}
            for col in translations[1].keys():
                return_dict[col.get(TranslationColumns.ref_column)] = self.parse_json(json, translations, group_counter, value_counter, col)
            return return_dict
        else:
            entity_list = translations[after_group]
            if col_entity is not None:
                entity_list = entity_list[col_entity]
            if entity_list[translation_index].get(TranslationValues.value) is None:
                return_values = []
                for json_value in json:
                    inner_result = self.parse_json(json_value, translations, group_counter, value_counter, col_entity)
                    if isinstance(inner_result, list):
                        return_values.extend(inner_result)
                    else:
                        return_values.append(inner_result)
                return return_values
            elif entity_list[translation_index].get(TranslationValues.is_url):
                url_var = entity_list[translation_index].get(TranslationValues.value)
                url_var = url_var.replace("%", str(json))
                new_json = self.web_manager.get(url_var)
                return self.parse_json(new_json, translations, group_counter, value_counter, col_entity)
            else:
                new_json = json[entity_list[translation_index].get(TranslationValues.value)]
                return self.parse_json(new_json, translations, group_counter, value_counter, col_entity)

    def get_translations(self, table):
        translation_table = self.get_translation_table(table)
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

    def get_translation_group_values(self, group_id):
        translation_group_select = database.entity(TranslationGroups)
        translation_group_select.add_where(TranslationGroups.id, group_id)
        return self.db_manager.select_all(translation_group_select)

    def get_translation_values(self, column_id):
        translation_value_select = database.entity(TranslationValues)
        translation_value_select.add_where(TranslationValues.column_id, column_id)
        translation_value_select.add_order_by(TranslationValues.value_no)
        return self.db_manager.select_all(translation_value_select)
