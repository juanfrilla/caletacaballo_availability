import time
import json

from utils import generate_12_months_list

from datetime import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests


def tokens_request(session: requests.Session):

    burp0_url = "https://www.booking.com:443/hotel/es/la-casita-del-mar-caleta-de-caballo.es.html"
    burp0_headers = {
        "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="136"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "es-ES,es;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=0, i",
        "Connection": "keep-alive",
    }
    response = session.get(burp0_url, headers=burp0_headers, impersonate="chrome136")
    return response


def set_cookies_request(session: requests.Session):

    burp0_url = "https://www.booking.com"
    burp0_headers = {
        "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="136"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "es-ES,es;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=0, i",
        "Connection": "keep-alive",
    }
    response = session.get(burp0_url, headers=burp0_headers, impersonate="chrome136")
    return response


def is_available(day_info):
    return day_info.get("minLengthOfStay") > 0


def check_availability_booking(
    session: requests.Session,
    tokens_json: dict,
    start_date=datetime.now().strftime("%Y-%m-%d"),
):
    burp0_url = "https://www.booking.com:443/dml/graphql?lang=es"
    burp0_headers = {
        "X-Booking-Topic": "capla_browser_b-property-web-property-page",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "X-Booking-Context-Action-Name": "hotel",
        "X-Booking-Context-Action": "hotel",
        "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="136"',
        "X-Booking-Site-Type-Id": "1",
        "Sec-Ch-Ua-Mobile": "?0",
        "X-Booking-Et-Serialized-State": tokens_json.get("etSerializedState"),
        "X-Booking-Dml-Cluster": "rust",
        "Accept": "*/*",
        "Apollographql-Client-Version": "aYGLBZDM",
        "Content-Type": "application/json",
        "Apollographql-Client-Name": "b-property-web-property-page_rust",
        "X-Booking-Csrf-Token": tokens_json.get("csrfToken"),
        "X-Booking-Context-Aid": "304142",
        "X-Apollo-Operation-Name": "AvailabilityCalendar",
        "X-Booking-Pageview-Id": "551f8741a6ab08a2",
        "Accept-Language": "es-ES,es;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Origin": "https://www.booking.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.booking.com/hotel/es/la-casita-del-mar-caleta-de-caballo.es.html",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=1, i",
    }
    burp0_json = {
        "extensions": {},
        "operationName": "AvailabilityCalendar",
        "query": "query AvailabilityCalendar($input: AvailabilityCalendarQueryInput!) {\n  availabilityCalendar(input: $input) {\n    ... on AvailabilityCalendarQueryResult {\n      hotelId\n      days {\n        available\n        avgPriceFormatted\n        checkin\n        minLengthOfStay\n        __typename\n      }\n      __typename\n    }\n    ... on AvailabilityCalendarQueryError {\n      message\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables": {
            "input": {
                "pagenameDetails": {
                    "countryCode": "es",
                    "pagename": "la-casita-del-mar-caleta-de-caballo",
                },
                "searchConfig": {
                    "childrenAges": [],
                    "nbAdults": 1,
                    "nbChildren": 0,
                    "nbRooms": 1,
                    "searchConfigDate": {"amountOfDays": 60, "startDate": start_date},
                },
                "travelPurpose": 2,
            }
        },
    }
    response = session.post(
        burp0_url, headers=burp0_headers, json=burp0_json, impersonate="chrome136"
    )
    return response.json()


def parse_tokens_json(soup: BeautifulSoup):
    script_tag = soup.find(
        "script", {"data-capla-application-context": "data-capla-application-context"}
    )
    if script_tag:
        json_text = script_tag.string.strip()
        return json.loads(json_text)


def create_booking_data(days: list):
    days_data = {}
    for day_info in days:
        result = is_available(day_info)
        checkin = day_info.get("checkin")
        days_data[checkin] = result
    return days_data


def scrape():
    session = requests.Session()
    days = []
    response = tokens_request(session)
    soup = BeautifulSoup(response.text, "html.parser")
    tokens_json = parse_tokens_json(soup)
    _12_months = generate_12_months_list()
    for date_str in _12_months:
        rjson = check_availability_booking(
            session=session, tokens_json=tokens_json, start_date=date_str
        )
        days_to_append = rjson.get("data").get("availabilityCalendar").get("days")
        days += days_to_append
    booking_data = create_booking_data(days)
    return booking_data
