import json

from bs4 import BeautifulSoup
from datetime import datetime
from curl_cffi import requests


def from_timestamp_to_human_readable(timestamp_ms):
    timestamp_s = timestamp_ms / 1000

    dt = datetime.fromtimestamp(timestamp_s)

    return dt.strftime("%d-%m-%Y")


def tokens_request():
    burp0_url = "https://www.airbnb.es:443/rooms/sw_skeleton"
    burp0_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Airbnb-Serviceworker": "true",
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.airbnb.es/sw-desktop_v4.js",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "es-ES,es;q=0.9",
        "Priority": "u=1, i",
    }
    response = requests.get(burp0_url, headers=burp0_headers, impersonate="chrome131")
    return response


def parse_tokens_json(soup: BeautifulSoup):
    script_tag = soup.find("script", {"id": "data-initializer-bootstrap"})
    if script_tag:
        json_text = script_tag.string.strip()
        return json.loads(json_text)


def check_availability(tokens_json):

    burp0_url = "https://www.airbnb.es:443/api/v3/PdpAvailabilityCalendar/8f08e03c7bd16fcad3c92a3592c19a8b559a0d0855a84028d1163d4733ed9ade?operationName=PdpAvailabilityCalendar&locale=es&currency=EUR&variables=%7B%22request%22%3A%7B%22count%22%3A12%2C%22listingId%22%3A%221188452677662328694%22%2C%22month%22%3A7%2C%22year%22%3A2025%7D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%228f08e03c7bd16fcad3c92a3592c19a8b559a0d0855a84028d1163d4733ed9ade%22%7D%7D"
    burp0_headers = {
        "X-Airbnb-Api-Key": tokens_json.get("layout-init").get("api_config").get("key"),
        "X-Airbnb-Supports-Airlock-V2": "true",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "X-Airbnb-Graphql-Platform-Client": "minimalist-niobe",
        "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="131"',
        "Sec-Ch-Dpr": "1",
        "Sec-Ch-Ua-Mobile": "?0",
        "X-Niobe-Short-Circuited": "true",
        "X-Airbnb-Graphql-Platform": "web",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Sec-Ch-Viewport-Width": "1920",
        "X-Csrf-Without-Token": "1",
        "X-Csrf-Token": "",
        "Ect": "4g",
        "Accept-Language": "es-ES,es;q=0.9",
        "Sec-Ch-Device-Memory": "8",
        "X-Airbnb-Client-Trace-Id": "10pgh0h0aqnmwc1w80rz618bglbp",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Client-Request-Id": "16n1fkl0ghh9io11nu2ps0wt6ijw",
        "X-Client-Version": tokens_json.get("layout-init").get("appVersionFull"),
        "Sec-Ch-Ua-Platform-Version": '""',
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.airbnb.es/rooms/1188452677662328694?source_impression_id=p3_1752396847_P3ES5q_QRpxSOYKQ",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=1, i",
    }
    response = requests.get(burp0_url, headers=burp0_headers, impersonate="chrome131")
    return response.json()


def create_airbnb_data(response_json: dict):
    days_data = {}
    months_data = (
        response_json.get("data")
        .get("merlin")
        .get("pdpAvailabilityCalendar")
        .get("calendarMonths")
    )
    for month_data in months_data:
        days = month_data.get("days")
        for day_info in days:
            date_str = day_info.get("calendarDate")
            available = day_info.get("available")
            days_data[date_str] = available
    return days_data


def scrape():
    tokens_response = tokens_request()
    soup = BeautifulSoup(tokens_response.text, "html.parser")
    tokens_json = parse_tokens_json(soup)
    response_json = check_availability(tokens_json)
    return create_airbnb_data(response_json)
