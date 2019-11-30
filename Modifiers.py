from datetime import datetime


def date_string_to_date(date_string):
    date_format = "%Y-%m-%d"
    return_date = datetime.strptime(date_string, date_format)
    return return_date


def height_string_to_int(height_string):
    feet = height_string.split("'")[0]
    inches = height_string.split("' ")[1].split('"')[0]
    height_int = int(feet) * 12 + int(inches)
    return height_int


modifiers = {'date_string_to_date': date_string_to_date,
             'height_string_to_int': height_string_to_int}