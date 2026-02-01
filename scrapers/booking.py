import json
from datetime import datetime

from bs4 import BeautifulSoup

from awswafsolver.client import AWSWAFSolver
from utils import generate_12_months_list


class BookingScraper:
    def __init__(self):
        target_url = "https://www.booking.com/hotel/es/la-casita-del-mar-caleta-de-caballo.es.html"
        self.chrome_version = "131"
        solver = AWSWAFSolver(target_url, self.chrome_version)
        self.session = solver.retrieve_session()

    def booking_request(self) -> str:
        url = "https://www.booking.com/hotel/es/la-casita-del-mar-caleta-de-caballo.es.html"
        headers = {
            "Ect": "4g",
            "Sec-Ch-Ua": f'"Not(A:Brand";v="8", "Chromium";v="{self.chrome_version}"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Accept-Language": "es-ES,es;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.chrome_version}.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": url,
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=0, i",
            "Connection": "keep-alive",
        }
        response = self.session.get(
            url,
            headers=headers,
            impersonate=f"chrome{self.chrome_version}",
        )
        return response

    def is_available(self, day_info):
        return day_info.get("minLengthOfStay") > 0

    def check_availability_booking(
        self,
        tokens_json: dict,
        start_date=datetime.now().strftime("%Y-%m-%d"),
    ):
        url = "https://www.booking.com/dml/graphql?lang=es"
        headers = {
            "X-Booking-Topic": "capla_browser_b-property-web-property-page",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "X-Booking-Context-Action-Name": "hotel",
            "X-Booking-Context-Action": "hotel",
            "Sec-Ch-Ua": f'"Not)A;Brand";v="8", "Chromium";v="{self.chrome_version}"',
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
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.chrome_version}.0.0.0 Safari/537.36",
            "Origin": "https://www.booking.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.booking.com/hotel/es/la-casita-del-mar-caleta-de-caballo.es.html",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i",
        }
        json = {
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
                        "searchConfigDate": {
                            "amountOfDays": 60,
                            "startDate": start_date,
                        },
                    },
                    "travelPurpose": 2,
                }
            },
        }
        response = self.session.post(
            url, headers=headers, json=json, impersonate=f"chrome{self.chrome_version}"
        )
        return response.json()

    def parse_tokens_json(self, soup: BeautifulSoup):
        script_tag = soup.find(
            "script",
            {"data-capla-application-context": "data-capla-application-context"},
        )
        if script_tag:
            json_text = script_tag.string.strip()
            return json.loads(json_text)

    def create_booking_data(self, days: list):
        days_data = {}
        for day_info in days:
            result = self.is_available(day_info)
            checkin = day_info.get("checkin")
            days_data[checkin] = result
        return days_data

    def scrape(self):
        days = []
        response = self.booking_request()
        soup = BeautifulSoup(response.text, "html.parser")
        tokens_json = self.parse_tokens_json(soup)
        _12_months = generate_12_months_list()
        for date_str in _12_months:
            rjson = self.check_availability_booking(
                tokens_json=tokens_json, start_date=date_str
            )
            days_to_append = rjson.get("data").get("availabilityCalendar").get("days")
            days += days_to_append
        booking_data = self.create_booking_data(days)
        return booking_data
