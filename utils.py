from datetime import datetime, date
import json


def generate_12_months_list(start_date=datetime.now().date()):
    months_list = []
    year = start_date.year
    month = start_date.month
    day = start_date.day

    for _ in range(12):
        months_list.append(date(year, month, day).strftime("%Y-%m-%d"))
        month += 1
        if month > 12:
            month = 1
            year += 1

    return months_list


def save_json(filename: str, data: dict):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)  # indent=4 is optional but makes it readable


def read_json(filename):
    with open(filename, "r") as f:
        info = json.loads(f.read())
        return info
