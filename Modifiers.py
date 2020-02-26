import logging
from datetime import datetime


class Modifier:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.date_format = "%Y-%m-%d"
        self.datetime_format = "%Y-%m-%d %H:%M:%S"

    def modify(self, modifier, args):
        modifier = self.modifiers[modifier]
        if isinstance(args, str):
            return_val = modifier(self, args)
        else:
            return_val = modifier(self, *args)
        return return_val

    def replace_string(self, string, new_substr, old_substr="%"):
        return_string = string
        if isinstance(new_substr, list):
            for new_val in new_substr:
                return_string = return_string.replace(old_substr, str(new_val), 1)
        else:
            return_string = return_string.replace(old_substr, str(new_substr))
        self.logger.info("Modified " + string + " to " + return_string)
        return return_string

    def date_string_to_date(self, date_string):
        return_date = datetime.strptime(date_string, self.date_format)
        self.logger.info("Modified " + date_string + " to " + str(return_date))
        return return_date

    def date_to_date_string(self, date):
        return_string = date.strftime(self.date_format)
        self.logger.info("Modified " + str(date) + " to " + return_string)
        return return_string

    def datetime_string_to_datetime(self, datetime_string):
        datetime_string = datetime_string.replace('T', ' ').replace('Z', '')
        return_datetime = datetime.strptime(datetime_string, self.datetime_format)
        self.logger.info("Modified " + datetime_string + " to " + str(return_datetime))
        return return_datetime

    def height_string_to_int(self, height_string):
        feet = height_string.split("'")[0]
        inches = height_string.split("' ")[1].split('"')[0]
        height_int = int(feet) * 12 + int(inches)
        self.logger.info("Modified " + height_string + " to " + str(height_int))
        return height_int

    def toi_to_sec(self, toi_string):
        minutes = toi_string.split(":")[0]
        seconds = toi_string.split(":")[1]
        seconds = int(seconds) + int(minutes) * 60
        self.logger.info("Modified " + toi_string + " to " + str(seconds))
        return seconds

    def immediate(self, val):
        if val == "True":
            self.logger.info("Parsed " + val + " as bool(True)")
            return True
        elif val == "False":
            self.logger.info("Parsed " + val + " as bool(False)")
            return False
        try:
            return_val = int(val)
            self.logger.info("Parsed " + val + " as int(" + str(return_val) + ")")
            return return_val
        except ValueError:
            self.logger.info("Could not parse " + val + " as bool or int")
            return val

    modifiers = {'replace_string': replace_string,
                 'date_string_to_date': date_string_to_date,
                 'height_string_to_int': height_string_to_int,
                 'datetime_string_to_datetime': datetime_string_to_datetime,
                 'toi_to_sec': toi_to_sec}
