import calendar
import json
from datetime import date, datetime


def generate_12_months_list(start_date=datetime.now().date()):
    months_list = []
    year = start_date.year
    month = start_date.month
    day = start_date.day

    for _ in range(12):
        last_day = calendar.monthrange(year, month)[1]
        valid_day = min(day, last_day)

        months_list.append(date(year, month, valid_day).strftime("%Y-%m-%d"))

        month += 1
        if month > 12:
            month = 1
            year += 1

    return months_list


def save_json(filename: str, data: dict):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def read_json(filename):
    with open(filename, "r") as f:
        info = json.loads(f.read())
        return info
